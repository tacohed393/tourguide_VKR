<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { MapLocation, Star, Search, User, Lock, Right } from '@element-plus/icons-vue'

// --- СОСТОЯНИЕ (Data) ---
const activeTab = ref('filters') 
const loading = ref(false)       
const places = ref([])           

// Поля ввода
const city = ref('Moscow')       
const category = ref('')
const price = ref('')
const aiQuery = ref('')

// Состояние модальных окон
const showDetails = ref(false)
const selectedPlace = ref(null)
const showWelcomeModal = ref(false) // Приветственное окно
const showAuthModal = ref(false)    // Окно логина/регистрации
const showProfile = ref(false)      // Окно профиля

// Авторизация
const token = ref(localStorage.getItem('token') || '')
const userEmail = ref(localStorage.getItem('userEmail') || '')
const authMode = ref('login')
const authForm = ref({ email: '', password: '' })
const favorites = ref([]) // ID избранных мест
const favoritesList = ref([]) // Полные объекты мест

// Вычисляемое свойство: вошел ли юзер
const isLoggedIn = computed(() => !!token.value)

// Списки данных
const cities = [
  { value: 'Moscow', label: 'Москва' },
  { value: 'Saint Petersburg', label: 'Санкт-Петербург' },
  { value: 'Omsk', label: 'Омск' }
]

const categories = [
  { value: 'Кафе', label: '☕ Кафе' },
  { value: 'Парк', label: '🌳 Парк' },
  { value: 'Музей', label: '🏛️ Музей' },
  { value: 'Бар', label: '🍸 Бар' }
]

const prices = [
  { value: 'Бесплатно', label: 'Бесплатно' },
  { value: 'Средний', label: 'Средний чек' },
  { value: 'Премиум', label: 'Премиум' }
]

// --- ИНИЦИАЛИЗАЦИЯ ---
onMounted(() => {
  // Если токена нет, показываем приветственное окно
  if (!token.value) {
    showWelcomeModal.value = true
  } else {
    // Если токен есть, настраиваем axios и грузим избранное
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    loadFavorites()
  }
})

// --- ЛОГИКА АВТОРИЗАЦИИ ---

// Открыть окно входа из приветствия
const openAuthFromWelcome = (mode) => {
  authMode.value = mode
  showWelcomeModal.value = false // Закрываем приветствие
  showAuthModal.value = true     // Открываем форму входа
}

// Продолжить как гость
const continueAsGuest = () => {
  showWelcomeModal.value = false
}

// Основная функция входа/регистрации
const handleAuth = async () => {
  try {
    let url = authMode.value === 'login' 
      ? 'http://localhost:8000/api/auth/login' 
      : 'http://localhost:8000/api/auth/register'
    
    let data;
    
    if (authMode.value === 'login') {
      const formData = new FormData();
      formData.append('username', authForm.value.email);
      formData.append('password', authForm.value.password);
      data = formData;
    } else {
      data = authForm.value;
    }

    const response = await axios.post(url, data);
    
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    userEmail.value = authForm.value.email
    localStorage.setItem('userEmail', userEmail.value)

    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    
    showAuthModal.value = false
    loadFavorites()
    
    // Если мы пришли из приветствия и успешно вошли, больше ничего не показываем
    
  } catch (e) {
    console.error(e)
    alert("Ошибка: " + (e.response?.data?.detail || "Сервер недоступен"))
  }
}

const logout = () => {
  token.value = ''
  userEmail.value = ''
  localStorage.removeItem('token')
  localStorage.removeItem('userEmail')
  favorites.value = []
  favoritesList.value = []
  delete axios.defaults.headers.common['Authorization']
  showProfile.value = false
  // При выходе снова показываем приветствие
  showWelcomeModal.value = true
}

// --- ЛОГИКА ИЗБРАННОГО ---

const loadFavorites = async () => {
  if (!isLoggedIn.value) return
  try {
    const res = await axios.get('http://localhost:8000/api/users/me')
    favoritesList.value = res.data.favorites
    favorites.value = res.data.favorites.map(p => p.id)
  } catch (e) {
    console.error("Ошибка загрузки профиля", e)
    if (e.response && e.response.status === 401) logout() // Токен протух
  }
}

const toggleFavorite = async (place) => {
  if (!isLoggedIn.value) {
    // Если гость нажал сердечко
    showAuthModal.value = true
    return
  }

  const isFav = favorites.value.includes(place.id)
  try {
    if (isFav) {
      await axios.delete(`http://localhost:8000/api/users/favorites/${place.id}`)
      favorites.value = favorites.value.filter(id => id !== place.id)
      favoritesList.value = favoritesList.value.filter(p => p.id !== place.id)
    } else {
      await axios.post(`http://localhost:8000/api/users/favorites/${place.id}`)
      favorites.value.push(place.id)
      favoritesList.value.push(place)
    }
  } catch (e) {
    alert("Ошибка при обновлении избранного")
  }
}

// --- ЛОГИКА ПОИСКА ---

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
    alert("Ошибка связи с сервером")
  } finally {
    loading.value = false
  }
}

const openPlaceDetails = (place) => {
  selectedPlace.value = place
  showDetails.value = true
}

const openMap = () => {
  if (selectedPlace.value) {
    if (selectedPlace.value.lat && selectedPlace.value.lon) {
      const { lat, lon, name, city } = selectedPlace.value
      const searchQuery = encodeURIComponent(`${city} ${name}`)
      const url = `https://2gis.ru/search/${searchQuery}/geo/${lon},${lat}?m=${lon}%2C${lat}%2F16`
      window.open(url, '_blank')
    } else {
      const searchQuery = encodeURIComponent(`${selectedPlace.value.city} ${selectedPlace.value.name}`)
      const url = `https://2gis.ru/search/${searchQuery}`
      window.open(url, '_blank')
    }
  }
}

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
    <header class="main-header-row">
      <div class="logo-area">
        <h1>TourGuide</h1>
      </div>
      
      <div class="user-menu">
        <!-- Если вошел: Показываем Email и Выход -->
        <div v-if="isLoggedIn" class="user-actions">
          <el-button type="info" plain @click="showProfile = true" :icon="User">
            {{ userEmail }}
          </el-button>
          <el-button type="danger" link @click="logout">Выйти</el-button>
        </div>

        <!-- Если гость: Показываем кнопку входа и заблокированный профиль -->
        <div v-else class="user-actions">
          <el-tooltip content="Войдите, чтобы открыть профиль" placement="bottom">
             <el-button type="info" disabled plain :icon="Lock">Гость</el-button>
          </el-tooltip>
          <el-button type="primary" @click="showAuthModal = true">Войти / Регистрация</el-button>
        </div>
      </div>
    </header>

    <div class="hero-text">
       <p>Твой персональный гид по культурным и интересным местам России</p>
    </div>

    <!-- SEARCH SECTION -->
    <el-card class="search-section" shadow="always">
      <el-tabs v-model="activeTab" stretch class="custom-tabs">
        <el-tab-pane name="filters">
          <template #label><el-icon><Search /></el-icon> Поиск по параметрам</template>
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

        <el-tab-pane name="ai">
          <template #label><el-icon><Star /></el-icon> Умный поиск (AI)</template>
          <div class="ai-box">
            <el-select v-model="city" placeholder="Город" size="large" style="margin-bottom: 15px; width: 200px;">
              <el-option v-for="item in cities" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-input
              v-model="aiQuery"
              type="textarea"
              :rows="2"
              placeholder="Опишите, чего вам хочется... (например: тихое историческое место для прогулки вечером)"
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
          <div class="image-wrapper">
             <img :src="place.image_url" class="card-img" loading="lazy" />
          </div>
          <div class="card-info">
            <div class="card-header-row">
              <h3>{{ place.name }}</h3>
              <el-tag type="success" size="small">{{ place.type }}</el-tag>
            </div>
            <p class="card-desc">{{ place.description.substring(0, 80) }}...</p>
            <div class="card-footer">
              <span>📍 {{ place.city }}</span>
              <span class="price-tag">{{ place.price }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- ============ МОДАЛЬНЫЕ ОКНА ============ -->

    <!-- 1. ПРИВЕТСТВЕННОЕ ОКНО (WELCOME) -->
    <el-dialog 
      v-model="showWelcomeModal" 
      width="450px" 
      align-center 
      :show-close="false" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="welcome-dialog"
    >
      <template #header>
        <div class="welcome-header">👋 Добро пожаловать!</div>
      </template>
      <div class="welcome-content">
        <p><b>TourGuide AI</b> — это умный помощник для поиска интересных мест.</p>
        <p>Вы можете использовать нейросеть для поиска по настроению или классические фильтры.</p>
        <p class="subtext">Чтобы пользоваться полным функционалом, пожалуйста, войдите.</p>
      </div>
      <template #footer>
        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="openAuthFromWelcome('login')" style="width: 100%">Войти</el-button>
          <el-button type="success" size="large" @click="openAuthFromWelcome('register')" style="width: 100%">Регистрация</el-button>
          <el-button type="info" link @click="continueAsGuest">Продолжить как гость <el-icon><Right /></el-icon></el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 2. ОКНО ВХОДА/РЕГИСТРАЦИИ -->
    <el-dialog v-model="showAuthModal" :title="authMode === 'login' ? 'Вход в систему' : 'Регистрация'" width="400px">
      <el-form label-position="top">
        <el-form-item label="Email">
          <el-input v-model="authForm.email" placeholder="example@mail.ru" />
        </el-form-item>
        <el-form-item label="Пароль">
          <el-input v-model="authForm.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="auth-footer">
          <el-button type="primary" @click="handleAuth" class="auth-submit-btn">
            {{ authMode === 'login' ? 'Войти' : 'Создать аккаунт' }}
          </el-button>
          
          <el-button @click="authMode = authMode === 'login' ? 'register' : 'login'" link>
            {{ authMode === 'login' ? 'Нет аккаунта? Регистрация' : 'Есть аккаунт? Вход' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 3. ЛИЧНЫЙ КАБИНЕТ -->
    <el-dialog v-model="showProfile" title="Личный кабинет" width="600px">
      <h3>⭐ Ваши избранные места:</h3>
      <div v-if="favoritesList.length > 0" class="fav-list">
        <div v-for="place in favoritesList" :key="place.id" class="fav-item" @click="openPlaceDetails(place)">
          <div class="fav-img-box">
             <img :src="place.image_url" class="fav-img"/>
          </div>
          <div class="fav-info">
            <b>{{ place.name }}</b>
            <div class="fav-meta"><small>{{ place.city }} • {{ place.type }}</small></div>
          </div>
          <el-button type="danger" :icon="Star" circle size="small" @click.stop="toggleFavorite(place)"></el-button>
        </div>
      </div>
      <el-empty v-else description="Вы еще ничего не добавили" />
    </el-dialog>

    <!-- 4. ДЕТАЛИ МЕСТА -->
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

          <!-- 
          <div class="ai-insight" v-if="selectedPlace.search_context">
            <strong>🤖 AI-анализ:</strong>
            <p>{{ selectedPlace.search_context }}</p>
          </div> 
          -->
          <el-divider content-position="left">Расположение на карте</el-divider>
          <div class="map-embed">
             <iframe 
               width="100%" 
               height="250" 
               frameborder="0" 
               style="border:0"
               :src="`https://yandex.ru/map-widget/v1/?ll=${selectedPlace.lon}%2C${selectedPlace.lat}&z=16&pt=${selectedPlace.lon}%2C${selectedPlace.lat},pm2rdl`"
               allowfullscreen
             ></iframe>
          </div>

          <div class="actions">
            <el-button type="primary" :icon="MapLocation" @click="openMap" size="large">В 2ГИС</el-button>
            
            <el-button 
                :type="favorites.includes(selectedPlace.id) ? 'warning' : 'default'" 
                :icon="Star" 
                @click="toggleFavorite(selectedPlace)" 
                size="large"
            >
                {{ favorites.includes(selectedPlace.id) ? 'В избранном' : 'В избранное' }}
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>

  </div>
</template>

<style scoped>
/* GENERAL LAYOUT */
.app-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8fafc;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}

/* HEADER */
.main-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.logo-area h1 { margin: 0; font-size: 1.8rem; color: #1e293b; font-weight: 800; }
.hero-text { text-align: center; margin-bottom: 40px; color: #64748b; }
.user-actions { display: flex; gap: 10px; align-items: center; }

/* SEARCH */
.search-section {
  border-radius: 20px;
  border: none;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}
.filters-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  padding: 20px 10px;
}
.ai-box { padding: 10px; }
.submit-area { text-align: center; margin-top: 10px; padding-bottom: 10px; }
.main-btn { width: 260px; height: 50px; font-weight: 800; border-radius: 25px; }

/* CARDS */
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
  overflow: hidden;
}
.place-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
.image-wrapper { width: 100%; height: 200px; overflow: hidden; }
.card-img { width: 100%; height: 100%; object-fit: cover; }
.card-info { padding: 20px; }
.card-header-row { display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }
.card-header-row h3 { margin: 0; font-size: 1.2rem; color: #1e293b; }
.card-desc { font-size: 14px; color: #64748b; line-height: 1.5; margin-bottom: 15px; }
.card-footer { display: flex; justify-content: space-between; font-size: 13px; color: #94a3b8; font-weight: 600; }

/* MODALS */
.welcome-header { font-size: 1.5rem; font-weight: bold; text-align: center; }
.welcome-content { text-align: center; font-size: 1.1rem; line-height: 1.6; }
.welcome-content .subtext { font-size: 0.9rem; color: #999; margin-top: 20px; }
.welcome-actions {
  display: flex;
  flex-direction: column; 
  gap: 15px;              
  padding: 0 20px;
  width: 100%;
  box-sizing: border-box;
}

/* кнопки растягиваться и убираем дурацкий отступ слева */
.welcome-actions .el-button {
  width: 100%;
  margin-left: 0 !important; 
  margin-right: 0 !important;
}

/* FAV LIST */
.fav-list { display: flex; flex-direction: column; gap: 10px; }
.fav-item { 
    display: flex; align-items: center; gap: 15px; padding: 10px; 
    border-radius: 8px; background: #fff; border: 1px solid #eee; cursor: pointer;
}
.fav-item:hover { background: #f9f9f9; }
.fav-img-box { width: 60px; height: 60px; border-radius: 8px; overflow: hidden; flex-shrink: 0; }
.fav-img { width: 100%; height: 100%; object-fit: cover; }
.fav-info { flex: 1; }
.fav-meta { color: #888; font-size: 0.9rem; }

/* DETAILS */
.map-embed { border-radius: 12px; overflow: hidden; margin-bottom: 20px; border: 1px solid #eee; }
.details-content { padding: 10px; }
.details-meta { margin-bottom: 15px; display: flex; gap: 10px; }
.details-title { font-size: 2rem; color: #1e293b; margin-bottom: 15px; }
.details-text { line-height: 1.7; color: #334155; font-size: 1.1rem; margin-bottom: 25px; }
.actions { display: flex; gap: 15px; justify-content: center; }

/* Футер модалки входа */
.auth-footer {
  display: flex;
  flex-direction: column; /* Кнопки друг под другом */
  align-items: center;    /* Выравнивание по центру */
  gap: 10px;              /* Отступ между кнопками */
  width: 100%;
}
/* Стили модалки */
.details-big-img { 
    width: 100%; 
    height: 250px; /* Фиксированная высота */
    object-fit: cover; 
    border-radius: 8px; 
    margin-bottom: 20px; /* Отступ от текста */
}
.auth-submit-btn {
  width: 100%;            /* Синяя кнопка на всю ширину */
}

/* САМОЕ ВАЖНОЕ: Убираем кривой отступ Element Plus */
.auth-footer .el-button + .el-button {
  margin-left: 0 !important;
}

@media (max-width: 768px) {
  .filters-grid { grid-template-columns: 1fr; }
  .main-header-row { flex-direction: column; gap: 15px; }
}
</style>