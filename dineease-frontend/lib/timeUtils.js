import { parse, format, isAfter, isBefore, isValid } from 'date-fns'

// Function to check if the clinic is open today
export const isOpenToday = (clinicOperationHours) => {
  const now = new Date()
  const todaySchedule = getTodaySchedule(clinicOperationHours)

  if (todaySchedule) {
    if (todaySchedule.time === 'Closed') {
      return false
    }

    if (todaySchedule.time === 'Open 24 hours') {
      return true
    }

    const timeRanges = Array.isArray(todaySchedule.time)
      ? todaySchedule.time
      : [todaySchedule.time]

    return timeRanges.some((range) => {
      const [openingHours, closingHours] = range.split(/\s*[-–]\s*/)
      const openingTime = parseTime(openingHours)
      const closingTime = parseTime(closingHours)

      return isAfter(now, openingTime) && isBefore(now, closingTime)
    })
  }

  return false
}

// Function to get today's closing time
export const getClosingTime = (clinicOperationHours) => {
  const todaySchedule = getTodaySchedule(clinicOperationHours)

  if (todaySchedule) {
    const scheduleTime = todaySchedule.time

    if (typeof scheduleTime === 'string') {
      const lowerCaseTime = scheduleTime.toLowerCase()

      if (lowerCaseTime.includes('closed')) {
        return 'Closed'
      }

      if (lowerCaseTime.includes('open 24 hours')) {
        return 'Open 24 hours'
      }

      if (lowerCaseTime.includes('holiday')) {
        return 'Closed Holiday'
      }
    }

    const timeRanges = Array.isArray(todaySchedule.time)
      ? todaySchedule.time
      : [todaySchedule.time]

    const closingTimes = timeRanges
      .map((range) => {
        if (typeof range === 'string') {
          const [, closingHours] = range.split(/\s*[-–]\s*/)
          return parseTime(closingHours)
        }
        return null
      })
      .filter(Boolean)

    if (closingTimes.length > 0) {
      const latestClosingTime = closingTimes.reduce((latest, current) =>
        isAfter(latest, current) ? latest : current
      )

      return format(latestClosingTime, 'h:mm a')
    }
  }

  return 'Closed'
}

// Function to get today's schedule
export const getTodaySchedule = (clinicOperationHours) => {
  if (!clinicOperationHours) {
    return null
  }

  const hoursArray = Object.entries(clinicOperationHours).map(([day, time]) => ({
    day: day.trim(),
    time: formatTimeString(time),
  }))

  const currentDay = getCurrentDay()

  const todaySchedule = hoursArray.find((pair) => pair.day.startsWith(currentDay)) || null

  if (!todaySchedule) {
    return null
  }

  const timeRanges = todaySchedule.time.split(/\s*(?:and|,)\s*/i)

  return {
    day: todaySchedule.day,
    time: timeRanges.length === 1 ? timeRanges[0] : timeRanges,
  }
}

// Function to format time strings
export const formatTimeString = (time) => {
  if (
    time.toLowerCase().includes('closed') ||
    time.toLowerCase().includes('open 24 hours')
  ) {
    return time.trim()
  }

  return time
    .replace(/^[a-zA-Z]+\s*/, '')
    .replace(/ – | - | –|– |–| -|-/g, '-')
    .replace(/\sto\s/gi, ' - ')
    .replace(/\s?([AaPp])\.?([Mm])\.?/g, ' $1$2')
    .replace(/\s+/g, ' ')
    .trim()
    .toUpperCase()
}

// Function to parse time strings
export const parseTime = (timeString) => {
  const formats = [
    'HH:mm:ss', // 08:00:00
    'h:mm a',   // 8:00 AM
    'h a',      // 8 AM
    'HH:mm',    // 08:00
  ]

  for (const formatStr of formats) {
    const parsedTime = parse(timeString, formatStr, new Date())
    if (isValid(parsedTime)) {
      return parsedTime
    }
  }

  console.error(`Invalid time format: ${timeString}`)
  return null
}

// Function to get the current day name (e.g., "Monday")
export const getCurrentDay = () => {
  return format(new Date(), 'EEEE')
}

// Get the current year
export const currentYear = new Date().getFullYear()

const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export const sortedOperatingHours = (operatingHours) => {
  return Object.entries(operatingHours)
    .sort(([dayA], [dayB]) => dayOrder.indexOf(dayA) - dayOrder.indexOf(dayB))
    .reduce((acc, [day, hours]) => {
      acc[day] = hours
      return acc
    }, {})
}