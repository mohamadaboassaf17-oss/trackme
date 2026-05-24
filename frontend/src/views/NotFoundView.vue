<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h2>الصفحة غير موجودة</h2>
      <p>الرابط الذي تبحث عنه غير موجود أو تم نقله</p>
      <router-link to="/dashboard" class="btn-primary">
        🏠 العودة للرئيسية
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView'
}
</script>

<style scoped>
.not-found-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 24px;
}
.not-found-content {
  max-width: 420px;
}
.error-code {
  font-size: 8rem;
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 16px;
}
h2 {
  color: var(--text-primary);
  margin-bottom: 8px;
}
p {
  color: var(--text-secondary);
  margin-bottom: 24px;
}
</style>
