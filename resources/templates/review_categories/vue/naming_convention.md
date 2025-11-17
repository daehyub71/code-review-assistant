# 네이밍 규칙 - Vue.js

## What to Check

- **컴포넌트명 규칙 위반**
  - PascalCase 미사용
  - 단일 단어 컴포넌트명

## Best Practices

### 1. 컴포넌트: PascalCase
```vue
<!-- Bad -->
<script>
export default {
  name: 'userCard'  // ❌
}
</script>

<!-- Good -->
<script setup>
// UserCard.vue
defineOptions({
  name: 'UserCard'  // ✅
})
</script>
```

### 2. Props/Events: camelCase
```vue
<script setup lang="ts">
// Props: camelCase
const props = defineProps<{
  userId: number
  isActive: boolean
}>()

// Events: camelCase
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'userSelected', id: number): void
}>()
</script>
```

### 3. Composables: use + PascalCase
```typescript
// useUserData.ts
export function useUserData() {
  // ...
}
```

## Vue 네이밍 규칙 요약

| 타입 | 규칙 | 예시 |
|------|------|------|
| 컴포넌트 | PascalCase | `UserCard.vue` |
| Props | camelCase | `userId`, `isActive` |
| Events | kebab-case (템플릿) | `@user-selected` |
| Composables | use + PascalCase | `useUserData` |

## References

- [Style Guide](https://vuejs.org/style-guide/)
