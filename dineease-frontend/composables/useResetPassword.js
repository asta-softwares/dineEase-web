export function useResetPasswordEndpoints() {
  const config = useRuntimeConfig();
  const baseUrl = config.public.apiBaseUrl;

  const findAccount = async (identifier) => {
    const { data, error } = await useFetch(`${baseUrl}find-account/`, {
      method: 'POST',
      body: { identifier },
    });

    if (error.value) throw error.value;
    
    localStorage.setItem('resetIdentifier', data.value.email);
    return data.value;
  };

  const resetPassword = async (identifier, code, newPassword) => {
    const { data, error } = await useFetch(`${baseUrl}reset-password/`, {
      method: 'POST',
      body: {
        identifier, // NOTE: always use email returned from findAccount
        code,
        new_password: newPassword,
      },
    });

    if (error.value) throw error.value;

    localStorage.removeItem('resetIdentifier');
    return data.value;
  };

  const resendResetCode = async (identifier) => {
    const { data, error } = await useFetch(`${baseUrl}resend-reset-code/`, {
      method: 'POST',
      body: { identifier }, // NOTE: always use email returned from findAccount
    });

    if (error.value) throw error.value;
    return data.value;
  };

  return {
    findAccount,
    resetPassword,
    resendResetCode,
  };
}
