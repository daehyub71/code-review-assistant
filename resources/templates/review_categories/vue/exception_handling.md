# 예외/에러 처리 - Vue.js

## What to Check

- **try-catch 누락**
  - async 함수에서 에러 처리 없음
  - API 호출 실패 시 처리 없음

- **에러 경계 없음**
  - 컴포넌트 에러가 상위로 전파
  - onErrorCaptured 미사용

## Best Practices

### 1. Async 에러 처리
```vue
<script setup lang="ts">
import { ref } from 'vue'

const loading = ref(false)
const error = ref<string | null>(null)

// Bad
async function fetchData() {
  const response = await fetch('/api/users')
  data.value = await response.json()  // 에러 처리 없음
}

// Good
async function fetchData() {
  loading.value = true
  error.value = null

  try {
    const response = await fetch('/api/users')

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    data.value = await response.json()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unknown error'
    console.error('Failed to fetch data:', e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error" class="error">{{ error }}</div>
  <div v-else>{{ data }}</div>
</template>
```

### 2. onErrorCaptured (에러 경계)
```vue
<script setup lang="ts">
import { onErrorCaptured, ref } from 'vue'

const hasError = ref(false)
const errorMessage = ref('')

onErrorCaptured((err, instance, info) => {
  hasError.value = true
  errorMessage.value = err.message
  console.error('Error captured:', err, info)
  return false  // 상위로 전파 중단
})
</script>

<template>
  <div v-if="hasError" class="error-boundary">
    <h2>Something went wrong</h2>
    <p>{{ errorMessage }}</p>
  </div>
  <slot v-else />
</template>
```

### 3. Global Error Handler
```typescript
// main.ts
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  // 에러 리포팅 서비스로 전송
}
```

## References

- [Error Handling](https://vuejs.org/api/composition-api-lifecycle.html#onerrorcaptured)
- [Global Error Handler](https://vuejs.org/api/application.html#app-config-errorhandler)
