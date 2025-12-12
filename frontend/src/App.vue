<script setup>
import { ref } from 'vue'
import axios from 'axios'

// --- Данные (State) ---
const query = ref('')           
const city = ref('Moscow')        
const places = ref([])          
const loading = ref(false)      

// --- Логика (Functions) ---
const handleSearch = async () => {
  if (!query.value) return 
  
  loading.value = true
  places.value = [] 

  try {
    const response = await axios.post('http://localhost:8000/places/search', {
      query: query.value,
      city: city.value,
      limit: 5
    })
    
    places.value = response.data
    
  } catch (error) {
    console.error(error)
    alert('Сервер не отвечает.')
  } finally {
    loading.value = false 
  }
}
</script>

<template>
  <div class="app-container">
    
    <!-- Шапка -->
    <div class="header">
      <h1>TourGuide AI</h1>
      <p>Гибридный поиск туристических мест (SQL + Vector)</p>
    </div>

    <!-- Блок поиска -->
    <el-card class="search-card">
      <div class="search-row">
        
        <!-- Выпадающий список городов -->
        <el-select v-model="city" placeholder="Выберите город" size="large" style="width: 160px;">
          <el-option label="Москва" value="Moscow" />
          <el-option label="Питер" value="Saint Petersburg" />
          <el-option label="Омск" value="Omsk" />
        </el-select>

        <!-- Поле ввода текста -->
        <el-input
          v-model="query"
          placeholder="Например: хочу посидеть за ноутбуком и отдохнуть в тихой обстановке"
          size="large"
          @keyup.enter="handleSearch"
          class="search-input"
        />

        <!-- Кнопка поиска -->
        <el-button type="primary" size="large" :loading="loading" @click="handleSearch">
          Найти
        </el-button>
      </div>
    </el-card>

    <!-- Список результатов -->
    <div class="results-area">
      
      <!-- Если ничего не найдено или еще не искали -->
      <el-empty v-if="places.length === 0 && !loading" description="Введите запрос, чтобы найти интересные места" />

      <!-- Сетка карточек -->
      <div v-else class="places-grid">
        <el-card 
          v-for="place in places" 
          :key="place.id" 
          class="place-card" 
          shadow="hover"
        >
          <template #header>
            <div class="card-header">
              <span class="place-name">{{ place.name }}</span>
              <el-tag type="success">{{ place.type }}</el-tag>
            </div>
          </template>
          
          <div class="card-body">
            <p class="desc">{{ place.description }}</p>
            <div class="meta">
              <el-tag type="info" size="small" effect="plain"> {{ place.city }}</el-tag>
            </div>
          </div>
        </el-card>
      </div>
    </div>

  </div>
</template>

<style>

/* Простые стили для красоты */
body {
  margin: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f0f2f5;
  color: #333;
}

.app-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  color: #409EFF; 
  margin: 0;
  font-size: 2.5rem;
}

.header p {
  color: #666;
  margin-top: 10px;
}

.search-card {
  margin-bottom: 30px;
  border-radius: 12px;
}

.search-row {
  display: flex;
  gap: 15px;
}

.search-input {
  flex: 1; 
}

.places-grid {
  display: grid;
  grid-template-columns: 1fr; 
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.place-name {
  font-weight: bold;
  font-size: 1.2rem;
}

.desc {
  line-height: 1.6;
  color: #555;
}

.meta {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}
</style>