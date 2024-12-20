export function useWebSocket(groupName, onMessageCallback) {
  const socket = ref(null);
  const notification = ref('');
  const config = useRuntimeConfig()

  const connectWebSocket = () => {
    const baseUrl = config.public.apiBaseUrl; // Get the base URL from config
    const wsProtocol = baseUrl.startsWith('https') ? 'wss://' : 'ws://';
    const host = new URL(baseUrl).host;
    const socketUrl = `${wsProtocol}${host}/ws/orders/${groupName}/`;

    console.log('Connecting to WebSocket:', socketUrl); // Debugging log

    socket.value = new WebSocket(socketUrl);

    socket.value.onopen = () => {
      console.log('WebSocket connected');
    };

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data);
      notification.value += `\n${data.message} (Status: ${data.status})`;
      if (onMessageCallback) {
        onMessageCallback(data);
      }
    };

    socket.value.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.value.onclose = () => {
      console.log('WebSocket closed');
    };
  };

  const closeWebSocket = () => {
    if (socket.value) {
      socket.value.close();
      console.log('WebSocket connection closed');
    }
  };

  return {
    socket,
    notification,
    connectWebSocket,
    closeWebSocket,
  };
}
