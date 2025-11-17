# 코드 문서화 - Vue.js

## What to Check

- **JSDoc 주석 누락**
  - 컴포넌트 설명 없음
  - Props 설명 없음

## Best Practices

### 1. 컴포넌트 JSDoc
```vue
<script setup lang="ts">
/**
 * 사용자 카드 컴포넌트
 * 
 * @example
 * <UserCard :user="user" @edit="handleEdit" />
 */

interface Props {
  /** 사용자 정보 */
  user: User
  /** 편집 가능 여부 */
  editable?: boolean
}

const props = defineProps<Props>()
</script>
```

### 2. Composable 문서화
```typescript
/**
 * 사용자 데이터 관리 composable
 * 
 * @example
 * const { user, loading, fetchUser } = useUserData()
 * await fetchUser(123)
 * 
 * @returns 사용자 데이터 및 관련 함수
 */
export function useUserData() {
  // ...
}
```

## References

- [TypeScript with Vue](https://vuejs.org/guide/typescript/overview.html)
