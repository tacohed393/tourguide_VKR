<script setup>
import { ref } from 'vue'
import axios from 'axios'

// --- СОСТОЯНИЕ ---
const activeTab = ref('filters') 
const loading = ref(false)       
const places = ref([])           

// Поля ввода
const city = ref('Moscow')       
const category = ref('')
const price = ref('')
const aiQuery = ref('')

const cities = [
  { value: 'Moscow', label: 'Москва' },
  { value: 'Saint Petersburg', label: 'Санкт-Петербург' },
  { value: 'Omsk', label: 'Омск' }
]

const categories = [
  { value: 'Кафе', label: 'Кафе' },
  { value: 'Парк', label: 'Парк' },
  { value: 'Музей', label: 'Музей' },
  { value: 'Бар', label: 'Бар' }
]

const prices = [
  { value: 'Бесплатно', label: 'Эконом' },
  { value: 'Средний', label: 'Средний' },
  { value: 'Премиум', label: 'Премиум' }
]

// --- ЛОГИКА ---
const handleSearch = async () => {
  if (!city.value) {
    alert("Пожалуйста, выберите город!")
    return
  }

  loading.value = true
  places.value = [] 

  try {
    let url = ''
    let payload = {}

    if (activeTab.value === 'filters') {
      url = 'http://localhost:8000/places/search/filters'
      payload = {
        city: city.value,
        type: category.value || null, 
        price: price.value || null,
        limit: 10
      }
    } else {
      url = 'http://localhost:8000/places/search/ai' 
      payload = {
        city: city.value,
        query: aiQuery.value,
        limit: 5
      }
    }

    const response = await axios.post(url, payload)
    places.value = response.data

  } catch (error) {
    console.error(error)
    alert("Ошибка связи с сервером")
  } finally {
    loading.value = false
  }
}

// Обработчик Enter в текстовом поле
const handleEnter = (e) => {
  if (!e.shiftKey) { 
    e.preventDefault() 
    handleSearch()     
  }
}
</script>

<template>
  <div class="app-layout">
    
    <!-- ЗАГОЛОВОК -->
    <div class="header">
      <h1>🌍 TourGuide AI</h1>
      <p>Найди идеальное место за секунду</p>
    </div>

    <!-- КАРТОЧКА ПОИСКА -->
    <el-card class="search-card">
      
      <!-- Вкладки -->
      <el-tabs v-model="activeTab" class="custom-tabs" stretch>
        
        <!-- Вкладка 1 -->
        <el-tab-pane label="ПОИСК ПО ПАРАМЕТРАМ" name="filters">
          <div class="filters-container">
            <div class="filter-item">
              <span class="label">Город</span>
              <el-select v-model="city" placeholder="Выберите город" size="large" style="width: 100%">
                <el-option v-for="c in cities" :key="c.value" :label="c.label" :value="c.value" />
              </el-select>
            </div>

            <div class="filter-item">
              <span class="label">Категория</span>
              <el-select v-model="category" placeholder="Любая" clearable size="large" style="width: 100%">
                <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
              </el-select>
            </div>

            <div class="filter-item">
              <span class="label">Бюджет</span>
              <el-select v-model="price" placeholder="Любой" clearable size="large" style="width: 100%">
                <el-option v-for="p in prices" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
            </div>
          </div>
        </el-tab-pane>

        <!-- Вкладка 2 -->
        <el-tab-pane label="УМНЫЙ ПОИСК (ИИ)" name="ai">
          <div class="ai-container">
            <div class="filter-item" style="margin-bottom: 20px;">
              <span class="label">Где искать?</span>
              <el-select v-model="city" placeholder="Выберите город" size="large" style="width: 100%">
                <el-option v-for="c in cities" :key="c.value" :label="c.label" :value="c.value" />
              </el-select>
            </div>
            
            <div class="filter-item">
              <span class="label">Ваши пожелания</span>
              <el-input
                v-model="aiQuery"
                :rows="2"
                type="textarea"
                placeholder="Например: хочу погулять в тишине у воды"
                resize="none"
                size="large"
                @keydown.enter="handleEnter"
              />
              <div class="hint">Нажмите Enter для поиска, Shift+Enter для переноса</div>
            </div>
          </div>
        </el-tab-pane>

      </el-tabs>

      <!-- БОЛЬШАЯ КНОПКА -->
      <div class="search-actions">
        <el-button type="primary" size="large" @click="handleSearch" :loading="loading" class="search-btn">
          НАЙТИ МЕСТА
        </el-button>
      </div>

    </el-card>

    <!-- РЕЗУЛЬТАТЫ -->
    <div class="results-container">
      <el-divider content-position="left">Результаты поиска</el-divider>

      <el-empty v-if="!loading && places.length === 0" description="Здесь появятся лучшие места..." />

      <div class="cards-grid">
        <el-card v-for="place in places" :key="place.id" class="place-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="place-title">{{ place.name }}</span>
              <el-tag type="success" effect="dark">{{ place.type }}</el-tag>
            </div>
          </template>
          
          <div class="card-body">
            <p class="place-desc">{{ place.description }}</p>
            <div class="place-footer">
              <el-tag type="info" effect="plain" size="small">📍 {{ place.city }}</el-tag>
              <el-tag type="warning" effect="plain" size="small">💰 {{ place.price || 'Не указано' }}</el-tag>
            </div>
          </div>
        </el-card>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* СТИЛИ */
.app-layout {
  max-width: 900px;
  margin: 0 auto;
  padding: 60px 20px;
  font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}
.header h1 {
  color: #2c3e50;
  font-size: 3rem;
  margin-bottom: 10px;
  font-weight: 800;
  letter-spacing: -1px;
}
.header p { color: #7f8c8d; font-size: 1.1rem; }

/* Карточка поиска */
.search-card {
  border-radius: 16px;
  margin-bottom: 50px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08) !important;
  border: none;
  overflow: hidden;
}

/* Вкладки (Tabs) */
.custom-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 600;
  height: 50px;
  color: #909399;
}
.custom-tabs :deep(.el-tabs__item.is-active) {
  color: #409EFF;
}

/* Контейнеры внутри вкладок */
.filters-container {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  padding: 20px 10px;
}

.ai-container {
  padding: 20px 10px;
  max-width: 600px; /* Ограничил ширину, чтобы не было слишком широко */
  margin: 0 auto;
}

.label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #34495e;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hint {
  margin-top: 5px;
  font-size: 12px;
  color: #999;
  text-align: right;
}

/* Кнопка */
.search-actions {
  margin-top: 10px;
  padding: 20px 10px 10px;
  text-align: center;
  border-top: 1px solid #f0f0f0;
}

.search-btn {
  width: 100%;
  max-width: 300px;
  height: 50px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  border-radius: 25px;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
}
.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

/* Результаты */
.cards-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}
.place-card {
  border-radius: 12px;
  border: 1px solid #eee;
  transition: transform 0.2s;
}
.place-card:hover {
  transform: translateY(-3px);
}
.place-title { font-weight: 700; font-size: 1.2rem; color: #2c3e50; }
.place-desc { color: #555; line-height: 1.6; margin-bottom: 20px; font-size: 1rem; }
.place-footer { display: flex; gap: 10px; }

/* Адаптив */
@media (max-width: 768px) {
  .filters-container {
    grid-template-columns: 1fr;
  }
  .header h1 { font-size: 2rem; }
}
</style>