# 설정 관리 - Vue.js

## What to Check

- **하드코딩된 값**
  - API URL 하드코딩
  - Magic Number/String

## Best Practices

### 1. 환경 변수
```bash
# .env
VITE_API_BASE_URL=https://api.example.com
VITE_API_TIMEOUT=30000

# .env.development
VITE_API_BASE_URL=http://localhost:3000

# .env.production
VITE_API_BASE_URL=https://prod-api.example.com
```

```typescript
// config.ts
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT),
}
```

### 2. 상수 정의
```typescript
// constants.ts
export const MAX_FILE_SIZE = 5 * 1024 * 1024  // 5MB
export const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png']
export const ITEMS_PER_PAGE = 20

// 사용
import { MAX_FILE_SIZE } from '@/constants'

if (file.size > MAX_FILE_SIZE) {
  // error
}
```

### 3. Provide/Inject for Config
```vue
<!-- App.vue -->
<script setup>
import { provide } from 'vue'

const config = {
  apiUrl: import.meta.env.VITE_API_URL,
  timeout: 30000,
}

provide('config', config)
</script>

<!-- Child.vue -->
<script setup>
import { inject } from 'vue'

const config = inject('config')
</script>
```

## References

- [Environment Variables (Vite)](https://vitejs.dev/guide/env-and-mode.html)
