<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { MapLocation, Star, Search, InfoFilled } from '@element-plus/icons-vue'

// --- СОСТОЯНИЕ (Data) ---
const activeTab = ref('filters') 
const loading = ref(false)       
const places = ref([])           

// Поля ввода
const city = ref('Moscow')       
const category = ref('')
const price = ref('')
const aiQuery = ref('')

// Состояние модального окна
const showDetails = ref(false)
const selectedPlace = ref(null)

// Списки для выпадающих меню (должны совпадать с seed.py)
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
  { value: 'Бесплатно', label: 'Бесплатно' },
  { value: 'Средний', label: 'Средний чек' },
  { value: 'Премиум', label: 'Премиум' }
]

// --- ЛОГИКА (Methods) ---

const handleSearch = async () => {
  if (!city.value) {
    alert("Пожалуйста, выберите город")
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
    console.error("Search Error:", error)
    alert("Ошибка связи с сервером. Проверьте запущен ли бэкенд.")
  } finally {
    loading.value = false
  }
}

// Открыть модалку
const openPlaceDetails = (place) => {
  selectedPlace.value = place
  showDetails.value = true
}

// Открыть Яндекс.Карты
const openMap = () => {
  // Проверяем, выбрано ли место и есть ли у него координаты
  if (selectedPlace.value && selectedPlace.value.lat && selectedPlace.value.lon) {
    
    const { lat, lon, name, city } = selectedPlace.value
    
    // Формируем "умную" ссылку для 2ГИС. 
    // Она сразу откроет поиск по названию в конкретном городе и сфокусирует карту по координатам.
    const searchQuery = encodeURIComponent(`${city} ${name}`)
    const url = `https://2gis.ru/search/${searchQuery}/geo/${lon},${lat}?m=${lon}%2C${lat}%2F16`
    
    window.open(url, '_blank')
    
  } else {
    // План Б: если вдруг координат в базе нет, просто ищем по названию
    const searchQuery = encodeURIComponent(`${selectedPlace.value.city} ${selectedPlace.value.name}`)
    const url = `https://2gis.ru/search/${searchQuery}`
    window.open(url, '_blank')
  }
}

// Обработка Enter в ИИ поиске
const handleAIEnter = (e) => {
  if (!e.shiftKey) {
    e.preventDefault()
    handleSearch()
  }
}
</script>

<template>
  <div class="app-container">
    
    <!-- HEADER -->
    <header class="main-header">
      <h1>TourGuide</h1>
      <p>Твой персональный гид по культурным и интересным местам России</p>
    </header>

    <!-- SEARCH SECTION -->
    <el-card class="search-section" shadow="always">
      <el-tabs v-model="activeTab" stretch class="custom-tabs">
        
        <!-- РЕЖИМ 1: ФИЛЬТРЫ -->
        <el-tab-pane name="filters">
          <template #label>
            Поиск по фильтрам
          </template>
          <div class="filters-grid">
            <div class="input-group">
              <label>Город</label>
              <el-select v-model="city" placeholder="Выбрать город" size="large">
                <el-option v-for="item in cities" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </div>
            <div class="input-group">
              <label>Тип места</label>
              <el-select v-model="category" placeholder="Любой" clearable size="large">
                <el-option v-for="item in categories" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </div>
            <div class="input-group">
              <label>Бюджет</label>
              <el-select v-model="price" placeholder="Любой" clearable size="large">
                <el-option v-for="item in prices" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </div>
          </div>
        </el-tab-pane>

        <!-- РЕЖИМ 2: ИИ ПОИСК -->
        <el-tab-pane name="ai">
          <template #label>
             Умный поиск
          </template>
          <div class="ai-box">
            <el-select v-model="city" placeholder="Город" size="large" style="margin-bottom: 15px; width: 200px;">
              <el-option v-for="item in cities" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-input
              v-model="aiQuery"
              type="textarea"
              :rows="2"
              placeholder="Опишите, чего вам хочется"
              @keydown.enter="handleAIEnter"
              resize="none"
            />
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="submit-area">
        <el-button type="primary" size="large" :loading="loading" @click="handleSearch" class="main-btn">
          НАЙТИ ЛОКАЦИИ
        </el-button>
      </div>
    </el-card>

    <!-- RESULTS SECTION -->
    <div class="results-area">
      <el-divider v-if="places.length > 0">Найдено для вас</el-divider>
      
      <el-empty v-if="places.length === 0 && !loading" description="Введите запрос, чтобы начать" />

      <div class="places-grid">
        <el-card 
          v-for="place in places" 
          :key="place.id" 
          class="place-card" 
          :body-style="{ padding: '0px' }"
          @click="openPlaceDetails(place)"
        >
          <img :src="place.image_url" class="card-img" />
          <div class="card-info">
            <div class="card-header-row">
              <h3>{{ place.name }}</h3>
              <el-tag type="success" size="small">{{ place.type }}</el-tag>
            </div>
            <p class="card-desc">{{ place.description.substring(0, 80) }}...</p>
            <div class="card-footer">
              <span>{{ place.city }}</span>
              <span class="price-tag">{{ place.price }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- MODAL DETAILS -->
    <el-dialog v-model="showDetails" width="600px" align-center destroy-on-close class="rounded-dialog">
      <div v-if="selectedPlace" class="details-body">
        <img :src="selectedPlace.image_url" class="details-big-img" />
        
        <div class="details-content">
          <div class="details-meta">
            <el-tag type="success" effect="dark">{{ selectedPlace.type }}</el-tag>
            <el-tag type="warning" effect="dark">{{ selectedPlace.price }}</el-tag>
          </div>
          
          <h2 class="details-title">{{ selectedPlace.name }}</h2>
          <p class="details-text">{{ selectedPlace.description }}</p>
          <!-- пока не надо 
          <div class="ai-insight" v-if="selectedPlace.search_context"> 
            <strong>AI-анализ атмосферы:</strong>
            <p>{{ selectedPlace.search_context }}</p>
          </div>
          -->
          <div class="actions">
            <el-button type="primary" :icon="MapLocation" @click="openMap" size="large">Показать на карте</el-button>
            <el-button type="danger" :icon="Star" plain size="large" @click="alert('Нужна авторизация')">В избранное</el-button>
          </div>
        </div>
      </div>
    </el-dialog>

  </div>
</template>

<style scoped>
.app-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
  background-color: #f8fafc;
  min-height: 100vh;
}

.main-header {
  text-align: center;
  margin-bottom: 40px;
}
.main-header h1 { font-size: 2.8rem; color: #1e293b; margin-bottom: 10px; font-weight: 800; }
.main-header p { color: #64748b; font-size: 1.1rem; }

.search-section {
  border-radius: 20px;
  padding: 10px;
  border: none;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  padding: 20px 10px;
}

.input-group label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  margin-bottom: 8px;
  padding-left: 2px;
}

.ai-box { padding: 10px; }

.submit-area {
  text-align: center;
  margin-top: 10px;
  padding-bottom: 10px;
}

.main-btn {
  width: 260px;
  height: 50px;
  font-weight: 800;
  border-radius: 25px;
  letter-spacing: 1px;
}

.places-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.place-card {
  border-radius: 16px;
  border: none;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}
.place-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }

.card-img { width: 100%; height: 200px; object-fit: cover; }
.card-info { padding: 20px; }
.card-header-row { display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }
.card-header-row h3 { margin: 0; font-size: 1.2rem; color: #1e293b; }
.card-desc { font-size: 14px; color: #64748b; line-height: 1.5; margin-bottom: 15px; }
.card-footer { display: flex; justify-content: space-between; font-size: 13px; color: #94a3b8; font-weight: 600; }

.details-big-img { width: 100%; height: 300px; object-fit: cover; border-radius: 12px; }
.details-content { padding-top: 20px; }
.details-meta { margin-bottom: 15px; display: flex; gap: 10px; }
.details-title { font-size: 2rem; color: #1e293b; margin-bottom: 15px; }
.details-text { line-height: 1.7; color: #334155; font-size: 1.1rem; margin-bottom: 25px; }
.ai-insight { background: #f1f5f9; padding: 15px; border-radius: 10px; margin-bottom: 25px; }
.ai-insight p { margin-top: 5px; font-size: 14px; color: #475569; }

.actions { display: flex; gap: 15px; justify-content: center; }

@media (max-width: 768px) {
  .filters-grid { grid-template-columns: 1fr; }
}
</style>