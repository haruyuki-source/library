<script setup>
import { ref, onMounted } from 'vue'
import { getStudentProfileApi } from '@/api/student'

// 学生端个人信息:只读展示
const loading = ref(false)
const profile = ref(null)

function genderText(v) {
  return { male: '男', female: '女', other: '其他' }[v] || v || '-'
}

onMounted(async () => {
  loading.value = true
  try {
    profile.value = await getStudentProfileApi()
  } catch (err) {
    profile.value = null
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <el-card v-loading="loading" shadow="never">
    <template #header>
      <span class="card-title">个人信息</span>
    </template>
    <el-descriptions v-if="profile" :column="2" border>
      <el-descriptions-item label="借书证号">{{ profile.card_no }}</el-descriptions-item>
      <el-descriptions-item label="姓名">{{ profile.name }}</el-descriptions-item>
      <el-descriptions-item label="性别">{{ genderText(profile.gender) }}</el-descriptions-item>
      <el-descriptions-item label="学院/部门">{{ profile.department || '-' }}</el-descriptions-item>
      <el-descriptions-item label="手机">{{ profile.phone || '-' }}</el-descriptions-item>
      <el-descriptions-item label="邮箱">{{ profile.email || '-' }}</el-descriptions-item>
      <el-descriptions-item label="最大可借数">{{ profile.max_borrow }} 本</el-descriptions-item>
      <el-descriptions-item label="注册时间">{{ (profile.created_at || '').slice(0, 10) || '-' }}</el-descriptions-item>
    </el-descriptions>
    <el-empty v-else-if="!loading" description="暂无信息" />
  </el-card>
</template>

<style scoped>
.card-title {
  color: #880e4f;
  font-weight: 600;
}
</style>
