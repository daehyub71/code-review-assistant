# Null/Undefined 안전성 - Vue.js

## What to Check

- **Optional Chaining 미사용**
  - obj.prop.subprop 직접 접근
  - null/undefined 체크 없음
  - v-if 가드 누락

- **TypeScript 미사용**
  - JavaScript만 사용
  - 타입 안전성 부족

## Best Practices

### 1. Optional Chaining (?.)
```vue
<!-- Bad -->
<template>
  <div>{{ user.profile.name }}</div>  <!-- user나 profile이 null이면 에러 -->
</template>

<!-- Good -->
<template>
  <div>{{ user?.profile?.name ?? 'Unknown' }}</div>
</template>
```

### 2. Nullish Coalescing (??)
```javascript
// Bad
const displayName = user.name || 'Guest'  // name이 ''일 때도 'Guest'

// Good
const displayName = user.name ?? 'Guest'  // null/undefined만 'Guest'
```

### 3. TypeScript + defineProps
```vue
<script setup lang="ts">
interface User {
  id: number
  name: string
  email?: string  // optional
}

interface Props {
  user?: User  // optional prop
  users: User[]  // required prop
}

const props = defineProps<Props>()

// 안전한 접근
const userName = props.user?.name ?? 'Anonymous'
</script>
```

### 4. Computed로 안전한 접근
```vue
<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ user?: User }>()

const safeUserName = computed(() => {
  return props.user?.name ?? 'Unknown'
})

const userEmail = computed(() => {
  if (!props.user) return null
  return props.user.email ?? 'No email'
})
</script>

<template>
  <div>{{ safeUserName }}</div>
</template>
```

### 5. v-if로 가드
```vue
<template>
  <!-- Bad -->
  <div>{{ user.profile.avatar }}</div>

  <!-- Good -->
  <div v-if="user?.profile">
    <img :src="user.profile.avatar" />
  </div>

  <!-- Better -->
  <template v-if="user?.profile?.avatar">
    <img :src="user.profile.avatar" />
  </template>
  <div v-else>No avatar</div>
</template>
```

## Example

**Before**:
```vue
<script>
export default {
  props: {
    user: Object
  },
  computed: {
    displayName() {
      return this.user.name  // user가 null이면 에러
    }
  }
}
</script>

<template>
  <div>
    <h1>{{ user.profile.name }}</h1>
    <p>{{ user.email }}</p>
  </div>
</template>
```

**After**:
```vue
<script setup lang="ts">
import { computed } from 'vue'

interface UserProfile {
  name: string
  avatar?: string
}

interface User {
  id: number
  name: string
  email?: string
  profile?: UserProfile
}

interface Props {
  user?: User
}

const props = defineProps<Props>()

const displayName = computed(() => {
  return props.user?.profile?.name ?? props.user?.name ?? 'Anonymous'
})

const hasEmail = computed(() => {
  return props.user?.email != null
})
</script>

<template>
  <div v-if="user">
    <h1>{{ displayName }}</h1>

    <p v-if="hasEmail">{{ user.email }}</p>
    <p v-else>No email provided</p>

    <img
      v-if="user.profile?.avatar"
      :src="user.profile.avatar"
      :alt="displayName"
    />
  </div>
  <div v-else>
    <p>User not found</p>
  </div>
</template>
```

## References

- [Optional Chaining (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [Nullish Coalescing (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)
- [Vue TypeScript](https://vuejs.org/guide/typescript/overview.html)
