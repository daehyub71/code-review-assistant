# 리소스 관리 - Vue.js

## What to Check

- **cleanup 함수 누락**
  - onUnmounted에서 정리 안 함
  - 이벤트 리스너 제거 안 함
  - 타이머 정리 안 함

## Best Practices

### 1. onUnmounted로 정리
```vue
<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

let intervalId: number

onMounted(() => {
  intervalId = setInterval(() => {
    // polling
  }, 1000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>
```

### 2. watchEffect cleanup
```vue
<script setup lang="ts">
import { watchEffect } from 'vue'

watchEffect((onCleanup) => {
  const controller = new AbortController()

  fetch('/api/data', { signal: controller.signal })

  onCleanup(() => {
    controller.abort()  // cleanup
  })
})
</script>
```

## References

- [Lifecycle Hooks](https://vuejs.org/api/composition-api-lifecycle.html)
