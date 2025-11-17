# 보안 모범 사례 - Vue.js

## What to Check

- **XSS 취약점**
  - v-html 사용
  - 사용자 입력 직접 렌더링

## Best Practices

### 1. v-html 대신 텍스트 바인딩
```vue
<!-- Bad - XSS 취약 -->
<div v-html="userInput"></div>

<!-- Good -->
<div>{{ userInput }}</div>  <!-- 자동 이스케이프 -->
```

### 2. DOMPurify로 sanitize
```vue
<script setup>
import DOMPurify from 'dompurify'
import { computed } from 'vue'

const props = defineProps<{ html: string }>()

const safeHtml = computed(() => 
  DOMPurify.sanitize(props.html)
)
</script>

<template>
  <div v-html="safeHtml"></div>
</template>
```

### 3. 환경 변수로 비밀 관리
```javascript
// .env
VITE_API_KEY=your_api_key

// 사용
const apiKey = import.meta.env.VITE_API_KEY
```

## References

- [Security](https://vuejs.org/guide/best-practices/security.html)
