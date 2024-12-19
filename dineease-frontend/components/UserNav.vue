<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" class="relative h-8 w-8 rounded-full">
        <Avatar class="h-8 w-8">
          <AvatarImage src="/avatars/01.png" alt="@shadcn" />
          <AvatarFallback>{{ initials }}</AvatarFallback>
        </Avatar>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent class="w-56" align="end">
      <DropdownMenuLabel class="font-normal flex">
        <div class="flex flex-col space-y-1">
          <p class="text-sm font-medium leading-none">
            {{ userStore.user.username }}
          </p>
          <p class="text-xs leading-none text-muted-foreground">
            {{ userStore.user.email }}
          </p>
        </div>
      </DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuGroup>
        <DropdownMenuItem as="div">
          <NuxtLink to="/account" class="flex items-center space-x-2 w-full">
            Account
          </NuxtLink>
        </DropdownMenuItem>
        <DropdownMenuItem as="div">
          <NuxtLink to="/profile" class="flex items-center space-x-2 w-full">
            Profile
          </NuxtLink>
        </DropdownMenuItem>
      </DropdownMenuGroup>
      <DropdownMenuSeparator />
      <DropdownMenuItem @click="handleLogout">
        Log out
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup>
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useUserStore } from '@/stores/user'
import { useAuthApi } from '@/composables/useAuthApi'
import { toast } from '@/components/ui/toast'

const userStore = useUserStore()
const router = useRouter()

const { logout } = useAuthApi()

const initials = computed(() => {
  const firstName = userStore.user?.first_name || ''
  const lastName = userStore.user?.last_name || ''
  const username = userStore.user?.username || ''

  if (firstName || lastName) {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
  }

  return username.slice(0, 2).toUpperCase()
})

// Method to handle logout
const handleLogout = async () => {
  try {
    await logout()
    toast({
      title: 'Logged Out Successfully!',
      description: 'You have been redirected to the login page.',
      variant: 'success',
    })
  } catch (error) {
    console.error("Logout failed:", error)
  }
}
</script>
