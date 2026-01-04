<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-left">
        <div class="login-left-content">
          <h1>资源管理器</h1>
          <p>计算资源集成系统</p>
          <div class="login-features">
            <div class="feature-item">
              <span class="feature-icon">🚀</span>
              <span>一键环境部署</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">📊</span>
              <span>实时资源监控</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">🛡️</span>
              <span>安全访问控制</span>
            </div>
          </div>
        </div>
      </div>
      <div class="login-right">
        <div class="login-form-container">
          <h2 class="form-title">欢迎回来</h2>
          <p class="form-subtitle">请登录您的账户</p>
          
          <a-form
            :model="formState"
            name="basic"
            layout="vertical"
            autocomplete="off"
            @finish="onFinish"
            @finishFailed="onFinishFailed"
            class="login-form"
          >
            <a-form-item
              label="用户名"
              name="username"
              :rules="[{ required: true, message: '请输入用户名！' }]"
            >
              <a-input v-model:value="formState.username" size="large" placeholder="admin">
                <template #prefix>
                  <span class="input-icon">👤</span>
                </template>
              </a-input>
            </a-form-item>

            <a-form-item
              label="密码"
              name="password"
              :rules="[{ required: true, message: '请输入密码！' }]"
            >
              <a-input-password v-model:value="formState.password" size="large" placeholder="password">
                <template #prefix>
                  <span class="input-icon">🔒</span>
                </template>
              </a-input-password>
            </a-form-item>

            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="loading" block size="large" class="submit-btn">
                登录
              </a-button>
            </a-form-item>

            <div class="form-footer">
              还没有账户？ <router-link to="/register">注册</router-link>
            </div>
          </a-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';

const authStore = useAuthStore();
const router = useRouter();
const loading = ref(false);

const formState = reactive({
  username: '',
  password: '',
});

const onFinish = async (values: any) => {
  loading.value = true;
  const success = await authStore.login(values);
  loading.value = false;
  if (success) {
    message.success('登录成功');
    router.push('/agents');
  } else {
    message.error('登录失败');
  }
};

const onFinishFailed = (errorInfo: any) => {
  console.log('Failed:', errorInfo);
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: stretch;
  padding: clamp(24px, 4vw, 48px);
  background: radial-gradient(circle at 15% 15%, rgba(255, 255, 255, 0.25), transparent 60%),
    linear-gradient(120deg, #0b63ff 0%, #001c4d 55%, #000b1f 100%);
}

.login-wrapper {
  flex: 1;
  display: flex;
  height: 100%;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 0;
  box-shadow: none;
  overflow: hidden;
  backdrop-filter: blur(6px);
}

.login-left {
  flex: 1.15;
  background: linear-gradient(200deg, rgba(255, 255, 255, 0.18) 0%, rgba(0, 0, 0, 0.1) 100%);
  padding: clamp(48px, 6vw, 96px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: white;
  position: relative;
}

.login-left::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.login-left-content {
  position: relative;
  z-index: 1;
}

.login-left h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 16px;
  color: white;
}

.login-left p {
  font-size: 18px;
  opacity: 0.8;
  margin-bottom: 40px;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 16px;
  opacity: 0.9;
}

.feature-icon {
  margin-right: 12px;
  font-size: 20px;
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(48px, 5vw, 96px);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
}

.login-form-container {
  width: 100%;
  max-width: 420px;
  padding: 48px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 24px 48px rgba(12, 28, 64, 0.18);
}

.form-title {
  font-size: 28px;
  font-weight: 600;
  color: #1f1f1f;
  margin-bottom: 8px;
}

.form-subtitle {
  color: #8c8c8c;
  margin-bottom: 32px;
}

.login-form :deep(.ant-form-item-label > label) {
  font-weight: 500;
}

.input-icon {
  color: #bfbfbf;
  font-size: 16px;
}

.submit-btn {
  height: 44px;
  font-size: 16px;
  margin-top: 16px;
  border-radius: 6px;
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  color: #8c8c8c;
}

@media (max-width: 768px) {
  .login-container {
    padding: 0;
  }

  .login-wrapper {
    width: 100%;
    height: 100%;
    border-radius: 0;
    flex-direction: column;
  }
  
  .login-left {
    flex: 0 0 auto;
    padding: 40px 24px;
  }
  
  .login-right {
    padding: 40px 24px;
    align-items: flex-start;
  }
}
</style>
