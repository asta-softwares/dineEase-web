const breadcrumbs = ref([
    { label: 'Dashboard', path: '/' },
]);

export const useBreadcrumb = () => {
  const setBreadcrumbs = (newBreadcrumbs) => {
    breadcrumbs.value = newBreadcrumbs;
  };

  return {
    breadcrumbs,
    setBreadcrumbs,
  };
};