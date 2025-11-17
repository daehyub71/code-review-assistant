# 성능 최적화 - Vue.js

## What to Check

- **불필요한 리렌더링**
  - computed 대신 method 사용
  - v-if/v-show 부적절한 사용
  - key 속성 누락

## Best Practices

### 1. computed vs method
```vue
<script setup>
import { computed } from 'vue'

// Bad - 매번 재계산
const total = () => items.value.reduce((sum, item) => sum + item.price, 0)

// Good - 캐시됨
const total = computed(() => 
  items.value.reduce((sum, item) => sum + item.price, 0)
)
</script>
```

### 2. v-show vs v-if
```vue
<!-- 자주 토글: v-show -->
<div v-show="isVisible">Frequent toggle</div>

<!-- 한 번만: v-if -->
<div v-if="isLoaded">Heavy component</div>
```

### 3. v-for with key
```vue
<!-- Bad -->
<div v-for="item in items">{{ item.name }}</div>

<!-- Good -->
<div v-for="item in items" :key="item.id">{{ item.name }}</div>
```

## References

- [Performance Best Practices](https://vuejs.org/guide/best-practices/performance.html)
