/**
 * EstateSphere - Client Application Core
 * Powers the interactive map, multi-agent AI suite, listings grid,
 * valuation engine, mortgage calculator, and tour booking.
 */

// Application State
const state = {
  properties: [],
  filteredProperties: [],
  selectedCity: 'all',
  filters: {
    type: 'all',
    maxPrice: 15000000,
    beds: 'any',
    search: '',
    sort: 'featured'
  },
  compareList: [],
  chatHistory: [],
  map: null,
  markers: {},
  activeMarkerId: null,
  charts: {
    history: null,
    mortgage: null
  }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  initMap();
  await loadProperties();
  await loadStats();
  await refreshToursCount();
  setupDefaultDates();
  checkUrlHashForProperty();
  lucide.createIcons();
});

function checkUrlHashForProperty() {
  const hash = window.location.hash;
  if (hash && hash.startsWith('#property-')) {
    const pid = parseInt(hash.replace('#property-', ''));
    if (!isNaN(pid)) {
      setTimeout(() => openPropertyModal(pid), 400);
    }
  }
}

function showToast(message, type = 'success') {
  let toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toastContainer';
    toastContainer.className = 'fixed top-16 right-6 z-50 flex flex-col space-y-2 pointer-events-none';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  const bgClass = type === 'success' 
    ? 'bg-dark-900/95 border-emerald-500/50 text-slate-100' 
    : 'bg-dark-900/95 border-rose-500/50 text-rose-300';
  const icon = type === 'success' ? 'check-circle-2' : 'alert-circle';
  const iconColor = type === 'success' ? 'text-emerald-400' : 'text-rose-400';

  toast.className = `p-3.5 px-4 rounded-2xl border ${bgClass} shadow-2xl backdrop-blur-md flex items-center space-x-2.5 text-xs font-semibold transform translate-y-2 opacity-0 transition-all duration-300 pointer-events-auto`;
  toast.innerHTML = `
    <i data-lucide="${icon}" class="w-4 h-4 ${iconColor} shrink-0"></i>
    <span>${message}</span>
  `;

  toastContainer.appendChild(toast);
  lucide.createIcons();

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('translate-y-2', 'opacity-0');
    setTimeout(() => toast.remove(), 350);
  }, 3200);
}

function copyPropertyLink(id) {
  const url = `${window.location.origin}/#property-${id}`;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(() => {
      showToast('Live Real Estate Link Copied to Clipboard!');
    }).catch(() => {
      prompt('Copy this live property link:', url);
    });
  } else {
    prompt('Copy this live property link:', url);
  }
}

// ============================================================================
// 1. LEAFLET MAP ENGINE
// ============================================================================
function initMap() {
  // Center on US view by default
  state.map = L.map('map', {
    zoomControl: false,
    attributionControl: false
  }).setView([37.0902, -95.7129], 4);

  // CartoDB Dark Matter free luxury tiles
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    subdomains: 'abcd'
  }).addTo(state.map);

  // Zoom control on top left
  L.control.zoom({ position: 'topleft' }).addTo(state.map);
}

function updateMapPins(properties) {
  // Clear existing markers
  Object.values(state.markers).forEach(m => state.map.removeLayer(m));
  state.markers = {};

  if (!properties || properties.length === 0) return;

  const bounds = L.latLngBounds();

  properties.forEach(p => {
    if (!p.lat || !p.lng) return;

    const formattedPrice = formatPriceAbbr(p.price);
    
    // Custom HTML Marker Icon
    const customIcon = L.divIcon({
      className: 'custom-pin-wrapper',
      html: `<div class="custom-price-pin" id="pin-${p.id}"><span>${formattedPrice}</span></div>`,
      iconSize: [60, 28],
      iconAnchor: [30, 14]
    });

    const marker = L.marker([p.lat, p.lng], { icon: customIcon }).addTo(state.map);

    // Popup Content
    const popupContent = `
      <div class="text-xs text-slate-100 w-52 p-1">
        <img src="${p.image_url}" class="w-full h-28 object-cover rounded-lg mb-2 shadow-sm" alt="${p.title}">
        <div class="font-bold text-sm text-gold-400 mb-0.5">$${p.price.toLocaleString()}</div>
        <div class="font-semibold text-slate-200 line-clamp-1 mb-1">${p.title}</div>
        <div class="text-[11px] text-slate-400 mb-2">${p.beds} Beds • ${p.baths} Baths • ${p.sqft.toLocaleString()} SqFt</div>
        <button onclick="openPropertyModal(${p.id})" class="w-full py-1.5 bg-gradient-to-r from-gold-500 to-amber-600 text-dark-950 font-bold rounded-md text-[11px] hover:brightness-110">
          View Property
        </button>
      </div>
    `;

    marker.bindPopup(popupContent, { maxWidth: 240, className: 'luxury-popup' });

    // Marker Interactions
    marker.on('click', () => {
      highlightActiveCard(p.id);
    });

    marker.on('mouseover', () => {
      highlightPin(p.id, true);
    });

    marker.on('mouseout', () => {
      if (state.activeMarkerId !== p.id) {
        highlightPin(p.id, false);
      }
    });

    state.markers[p.id] = marker;
    bounds.extend([p.lat, p.lng]);
  });

  // Fit bounds if we have valid locations
  if (properties.length > 0 && bounds.isValid()) {
    state.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
  }
}

function highlightPin(id, active) {
  const pinEl = document.getElementById(`pin-${id}`);
  if (pinEl) {
    if (active) {
      pinEl.classList.add('active-pin');
    } else {
      pinEl.classList.remove('active-pin');
    }
  }
}

function resetMapView() {
  if (state.filteredProperties.length > 0) {
    updateMapPins(state.filteredProperties);
  } else {
    updateMapPins(state.properties);
  }
}

// ============================================================================
// 2. DATA FETCHING & FILTER LOGIC
// ============================================================================
async function loadProperties() {
  try {
    const params = new URLSearchParams();
    if (state.selectedCity !== 'all') params.append('city', state.selectedCity);
    if (state.filters.type !== 'all') params.append('type', state.filters.type);
    if (state.filters.maxPrice) params.append('max_price', state.filters.maxPrice);
    if (state.filters.beds !== 'any') params.append('beds', state.filters.beds);
    if (state.filters.search) params.append('search', state.filters.search);
    if (state.filters.sort) params.append('sort', state.filters.sort);

    const res = await fetch(`/api/properties?${params.toString()}`);
    const data = await res.json();

    if (data.success) {
      state.properties = data.properties;
      state.filteredProperties = data.properties;
      renderPropertiesGrid(data.properties);
      updateMapPins(data.properties);
      populateAgentPropertySelects(data.properties);
      updateFavsBadge();
    }
  } catch (err) {
    console.error('Failed to load properties:', err);
  }
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    if (data.success) {
      document.getElementById('statTotalListings').textContent = data.total_properties;
      document.getElementById('statAvgPrice').textContent = `$${(data.average_price / 1000000).toFixed(1)}M`;
      document.getElementById('statAvgSqft').textContent = `$${data.avg_price_per_sqft}`;
    }
  } catch (e) {
    console.warn(e);
  }
}

function renderPropertiesGrid(properties) {
  const container = document.getElementById('propertiesGrid');
  const countEl = document.getElementById('resultsCount');

  countEl.textContent = `${properties.length} Premier Residence${properties.length === 1 ? '' : 's'} Found`;

  if (!properties || properties.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-16 text-center text-slate-400 space-y-3">
        <i data-lucide="home" class="w-10 h-10 mx-auto text-slate-600 stroke-[1.5]"></i>
        <p class="text-sm">No properties match your current filter parameters.</p>
        <button onclick="resetFilters()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-gold-400 font-semibold rounded-xl text-xs transition-all">
          Clear All Filters
        </button>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  container.innerHTML = properties.map(p => {
    const isCompared = state.compareList.some(item => item.id === p.id);
    const favClass = p.is_favorite ? 'text-rose-500 fill-rose-500' : 'text-slate-400 hover:text-white';

    return `
      <article 
        id="card-${p.id}"
        onmouseenter="handleCardHover(${p.id}, true)"
        onmouseleave="handleCardHover(${p.id}, false)"
        class="glass-card card-hover-effect rounded-2xl overflow-hidden flex flex-col justify-between border border-slate-800/80 group"
      >
        <!-- Top Image with Badges -->
        <div class="relative h-48 w-full overflow-hidden bg-slate-900">
          <img 
            src="${p.image_url}" 
            alt="${p.title}"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          >
          <div class="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent opacity-80"></div>
          
          <!-- Property Type Badge -->
          <div class="absolute top-3 left-3 px-2.5 py-1 rounded-md bg-dark-950/80 backdrop-blur-md border border-slate-700/80 text-[10px] font-bold uppercase tracking-wider text-gold-400">
            ${p.type}
          </div>

          <!-- Top Right Favorite & Compare Check -->
          <div class="absolute top-3 right-3 flex items-center space-x-1.5">
            <button 
              onclick="toggleFavorite(${p.id}, event)"
              class="w-8 h-8 rounded-full bg-dark-950/80 backdrop-blur-md flex items-center justify-center transition-all ${favClass}"
              title="Save to favorites"
            >
              <i data-lucide="heart" class="w-4 h-4"></i>
            </button>
          </div>

          <!-- Bottom Price inside image -->
          <div class="absolute bottom-3 left-3 right-3 flex items-baseline justify-between">
            <div class="text-xl font-extrabold text-white tracking-tight">
              $${p.price.toLocaleString()}
            </div>
            <div class="text-[11px] text-slate-300 font-medium">
              $${Math.round(p.price / p.sqft).toLocaleString()} / sqft
            </div>
          </div>
        </div>

        <!-- Details Body -->
        <div class="p-4 space-y-2.5 flex-1 flex flex-col justify-between">
          <div>
            <h3 class="font-bold text-sm text-slate-100 group-hover:text-gold-400 transition-colors line-clamp-1">
              ${p.title}
            </h3>
            <p class="text-xs text-slate-400 line-clamp-1 mt-0.5">
              ${p.address}, ${p.city}, ${p.state}
            </p>

            <!-- Key Specs Metric Bar -->
            <div class="flex items-center space-x-3 text-xs text-slate-300 py-2 border-y border-slate-800/80 mt-2.5">
              <span class="flex items-center space-x-1 font-medium">
                <i data-lucide="bed" class="w-3.5 h-3.5 text-gold-400"></i>
                <span>${p.beds} Beds</span>
              </span>
              <span>•</span>
              <span class="flex items-center space-x-1 font-medium">
                <i data-lucide="bath" class="w-3.5 h-3.5 text-gold-400"></i>
                <span>${p.baths} Baths</span>
              </span>
              <span>•</span>
              <span class="flex items-center space-x-1 font-medium">
                <i data-lucide="maximize" class="w-3.5 h-3.5 text-gold-400"></i>
                <span>${p.sqft.toLocaleString()} SqFt</span>
              </span>
            </div>

            <!-- Features Tags (up to 3) -->
            <div class="flex flex-wrap gap-1 mt-2.5">
              ${p.features.slice(0, 3).map(f => `
                <span class="px-2 py-0.5 rounded bg-dark-850 border border-slate-800 text-[10px] text-slate-400">
                  ${f}
                </span>
              `).join('')}
              ${p.features.length > 3 ? `
                <span class="px-1.5 py-0.5 text-[10px] text-slate-500">+${p.features.length - 3}</span>
              ` : ''}
            </div>

            <!-- Seller / Listing Agent Direct Contact Bar -->
            <div class="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2 min-w-0">
                <img src="${p.agent_avatar}" class="w-6 h-6 rounded-full object-cover border border-gold-500/50 shrink-0" alt="${p.agent_name}">
                <div class="truncate">
                  <span class="text-[9px] uppercase tracking-wider text-slate-400 font-bold block leading-none">Seller's Agent</span>
                  <span class="text-[11px] font-semibold text-slate-200 truncate">${p.agent_name}</span>
                </div>
              </div>
              <div class="flex items-center space-x-1.5 shrink-0">
                <a 
                  href="tel:${p.agent_phone}" 
                  onclick="event.stopPropagation()"
                  class="px-2.5 py-1 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[11px] font-bold flex items-center space-x-1 transition-all"
                  title="Call Seller Directly"
                >
                  <i data-lucide="phone-call" class="w-3 h-3"></i>
                  <span>Call Seller</span>
                </a>
                <a 
                  href="https://api.whatsapp.com/send?phone=${p.agent_phone.replace(/[^0-9]/g, '')}&text=${encodeURIComponent('Hello ' + p.agent_name + ', I am interested in viewing ' + p.title + ' listed at $' + p.price.toLocaleString() + ' on EstateSphere.')}"
                  target="_blank"
                  onclick="event.stopPropagation()"
                  class="p-1 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400 border border-emerald-500/30 transition-all"
                  title="Chat on WhatsApp with Seller"
                >
                  <i data-lucide="message-circle" class="w-3.5 h-3.5"></i>
                </a>
                <a 
                  href="mailto:${p.agent_email}?subject=Inquiry regarding ${encodeURIComponent(p.title)}" 
                  onclick="event.stopPropagation()"
                  class="p-1 rounded-lg bg-dark-850 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition-all"
                  title="Email Seller"
                >
                  <i data-lucide="mail" class="w-3.5 h-3.5"></i>
                </a>
              </div>
            </div>
          </div>

          <!-- Bottom Action Buttons -->
          <div class="pt-3 border-t border-slate-800/80 flex items-center space-x-2 text-xs">
            <button 
              onclick="openPropertyModal(${p.id})"
              class="flex-1 py-2 bg-dark-850 hover:bg-slate-800 border border-slate-700/80 text-slate-200 font-semibold rounded-xl transition-all text-center"
            >
              Details
            </button>
            <button 
              onclick="openApexForProperty(${p.id})"
              class="p-2 bg-dark-850 hover:bg-slate-800 border border-slate-700/80 text-emerald-400 rounded-xl transition-all"
              title="Run AVM Valuation Model"
            >
              <i data-lucide="trending-up" class="w-4 h-4"></i>
            </button>
            <button 
              onclick="openAtlasForProperty(${p.id})"
              class="p-2 bg-gradient-to-r from-gold-500 to-amber-600 text-dark-950 font-bold rounded-xl transition-all hover:brightness-110"
              title="Schedule Site Tour"
            >
              <i data-lucide="calendar" class="w-4 h-4"></i>
            </button>
            <button 
              onclick="toggleCompare(${p.id})"
              class="p-2 rounded-xl border ${isCompared ? 'bg-gold-500 text-dark-950 border-gold-400 font-bold' : 'bg-dark-850 text-slate-400 border-slate-800 hover:text-white'}"
              title="Compare side-by-side"
            >
              <i data-lucide="git-compare" class="w-4 h-4"></i>
            </button>
          </div>
        </div>
      </article>
    `;
  }).join('');

  lucide.createIcons();
}

function handleCardHover(id, isHovering) {
  highlightPin(id, isHovering);
  if (isHovering && state.markers[id]) {
    // Pan slightly towards marker if outside view
    const m = state.markers[id];
    if (!state.map.getBounds().contains(m.getLatLng())) {
      state.map.panTo(m.getLatLng(), { animate: true, duration: 0.5 });
    }
  }
}

function highlightActiveCard(id) {
  state.activeMarkerId = id;
  const card = document.getElementById(`card-${id}`);
  if (card) {
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    card.classList.add('ring-2', 'ring-gold-500');
    setTimeout(() => {
      card.classList.remove('ring-2', 'ring-gold-500');
    }, 2500);
  }
}

// ============================================================================
// 3. FILTER & SEARCH CONTROLS
// ============================================================================
function setCityFilter(city) {
  state.selectedCity = city;
  
  // Update city pills UI
  document.querySelectorAll('.city-pill').forEach(btn => {
    if (btn.dataset.city === city) {
      btn.className = 'city-pill px-3 py-1.5 text-xs font-semibold rounded-lg transition-all bg-gold-500 text-dark-950 shadow-md';
    } else {
      btn.className = 'city-pill px-3 py-1.5 text-xs font-medium rounded-lg transition-all text-slate-300 hover:text-white hover:bg-slate-800/60';
    }
  });

  applyFilters();
}

function updatePriceSlider(val) {
  const num = parseInt(val);
  state.filters.maxPrice = num;
  document.getElementById('maxPriceLabel').textContent = num >= 15000000 ? '$15.0M+' : `$${(num / 1000000).toFixed(1)}M`;
}

function applyFilters() {
  state.filters.type = document.getElementById('typeFilter').value;
  state.filters.beds = document.getElementById('bedsFilter').value;
  state.filters.sort = document.getElementById('sortFilter').value;
  loadProperties();
}

function handleSearchSubmit() {
  const query = document.getElementById('searchInput').value.trim();
  if (!query) {
    state.filters.search = '';
    applyFilters();
    return;
  }

  // If query is natural-language conversational, route to Aria
  if (query.split(' ').length > 3 || query.includes('under') || query.includes('with') || query.includes('near')) {
    toggleAgentDrawer(true);
    switchAgentTab('aria');
    sendAriaQuery(query);
  } else {
    state.filters.search = query;
    applyFilters();
  }
}

function triggerQuickPrompt(promptText) {
  document.getElementById('searchInput').value = promptText;
  toggleAgentDrawer(true);
  switchAgentTab('aria');
  sendAriaQuery(promptText);
}

function resetFilters() {
  state.selectedCity = 'all';
  state.filters = {
    type: 'all',
    maxPrice: 15000000,
    beds: 'any',
    search: '',
    sort: 'featured'
  };

  document.getElementById('searchInput').value = '';
  document.getElementById('typeFilter').value = 'all';
  document.getElementById('bedsFilter').value = 'any';
  document.getElementById('sortFilter').value = 'featured';
  document.getElementById('priceSlider').value = 15000000;
  document.getElementById('maxPriceLabel').textContent = '$15.0M';
  document.getElementById('activeCriteriaNote').textContent = '';

  document.querySelectorAll('.city-pill').forEach(btn => {
    btn.className = btn.dataset.city === 'all'
      ? 'city-pill px-3 py-1.5 text-xs font-semibold rounded-lg transition-all bg-gold-500 text-dark-950 shadow-md'
      : 'city-pill px-3 py-1.5 text-xs font-medium rounded-lg transition-all text-slate-300 hover:text-white hover:bg-slate-800/60';
  });

  loadProperties();
}

// ============================================================================
// 4. MULTI-AGENT SUITE (ARIA, APEX, ATLAS)
// ============================================================================
function toggleAgentDrawer(open) {
  const drawer = document.getElementById('agentDrawer');
  if (open) {
    drawer.classList.remove('translate-x-full');
  } else {
    drawer.classList.add('translate-x-full');
  }
}

function switchAgentTab(tab) {
  const tabs = ['aria', 'apex', 'atlas'];
  tabs.forEach(t => {
    const btn = document.getElementById(`tab${t.charAt(0).toUpperCase() + t.slice(1)}`);
    const content = document.getElementById(`agentContent${t.charAt(0).toUpperCase() + t.slice(1)}`);
    
    if (t === tab) {
      btn.className = 'flex-1 py-2 rounded-lg font-bold flex items-center justify-center space-x-1.5 transition-all bg-gold-500 text-dark-950 shadow-md';
      content.classList.remove('hidden');
    } else {
      btn.className = 'flex-1 py-2 rounded-lg font-bold flex items-center justify-center space-x-1.5 transition-all text-slate-400 hover:text-white hover:bg-slate-800/60';
      content.classList.add('hidden');
    }
  });

  if (tab === 'apex') {
    runApexValuation();
  }
}

// --- ARIA (AGENT 1: NATURAL LANGUAGE DISCOVERY) ---
function handleAriaSend() {
  const input = document.getElementById('ariaInput');
  const query = input.value.trim();
  if (!query) return;
  input.value = '';
  sendAriaQuery(query);
}

async function sendAriaQuery(query) {
  const transcript = document.getElementById('ariaChatTranscript');

  // User Message Bubble
  transcript.innerHTML += `
    <div class="flex items-start justify-end space-x-2">
      <div class="bg-gold-500/10 border border-gold-500/30 text-slate-100 rounded-2xl p-3 max-w-[85%] text-xs font-medium">
        ${escapeHtml(query)}
      </div>
    </div>
  `;

  // Typing indicator with RAG Status
  const typingId = `typing-${Date.now()}`;
  transcript.innerHTML += `
    <div id="${typingId}" class="flex items-center space-x-2 p-3 text-gold-400 text-xs">
      <i data-lucide="sparkles" class="w-3.5 h-3.5 animate-spin"></i>
      <span>Aria is considering your request...</span>
    </div>
  `;
  transcript.scrollTop = transcript.scrollHeight;
  lucide.createIcons();

  // Track multi-turn conversation
  state.chatHistory.push({ role: 'user', content: query });

  try {
    const res = await fetch('/api/agents/rag', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        history: state.chatHistory.slice(-8)
      })
    });
    const data = await res.json();
    document.getElementById(typingId)?.remove();

    if (data.success) {
      const result = data.result;
      state.chatHistory.push({ role: 'assistant', content: result.response });

      const recs = result.properties || [];
      const intent = result.action_intent;
      const actionData = result.action_data || {};
      const ragSources = result.rag_context_used || [];
      const aiStatus = result.source === 'Gemini'
        ? { label: 'Gemini AI', classes: 'bg-emerald-500/20 text-emerald-400' }
        : result.source === 'Gemini unavailable'
          ? { label: 'Gemini unavailable', classes: 'bg-rose-500/20 text-rose-300' }
          : result.source === 'Gemini setup required'
            ? { label: 'Setup required', classes: 'bg-amber-500/20 text-amber-300' }
            : ragSources.length > 0
              ? { label: 'RAG Grounded', classes: 'bg-emerald-500/20 text-emerald-400' }
              : { label: 'Consultation', classes: 'bg-slate-700 text-slate-300' };

      // Format markdown bold & line breaks
      let formattedText = escapeHtml(result.response)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');

      // RAG Citations Strip
      const ragCitationsHtml = ragSources.length > 0 ? `
        <div class="pt-2 border-t border-slate-800/80">
          <span class="text-[9px] uppercase tracking-wider text-slate-400 font-bold block mb-1 flex items-center space-x-1">
            <i data-lucide="database" class="w-3 h-3 text-gold-400"></i>
            <span>RAG Grounded Citations (${ragSources.length} Verified Sources)</span>
          </span>
          <div class="flex flex-wrap gap-1">
            ${ragSources.map(s => `
              <span class="px-2 py-0.5 rounded bg-dark-900 border border-slate-800 text-[9px] text-slate-300" title="${escapeHtml(s.excerpt)}">
                🏷️ ${escapeHtml(s.title)} (${Math.round(s.relevance_score * 100)}% match)
              </span>
            `).join('')}
          </div>
        </div>
      ` : '';

      // Autonomous Tool Action Cards
      let actionBoxHtml = '';
      if (intent === 'contact_seller' && actionData.seller_phone) {
        actionBoxHtml = `
          <div class="p-3.5 rounded-xl bg-gradient-to-br from-dark-900 to-slate-900 border border-emerald-500/40 space-y-2.5">
            <div class="flex items-center justify-between">
              <span class="text-[10px] uppercase font-bold text-emerald-400 flex items-center space-x-1">
                <i data-lucide="phone-call" class="w-3.5 h-3.5"></i>
                <span>Direct Seller Connection</span>
              </span>
              <span class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[9px] font-bold">Live Seller Line</span>
            </div>
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-full bg-gold-500/20 text-gold-400 flex items-center justify-center font-bold text-sm border border-gold-500/40 shrink-0">
                ${actionData.seller_name.charAt(0)}
              </div>
              <div class="min-w-0 flex-1">
                <h4 class="font-bold text-white text-xs truncate">${actionData.seller_name}</h4>
                <p class="text-[10px] text-slate-400 truncate">${actionData.property_title}</p>
                <p class="text-[11px] text-emerald-400 font-bold">${actionData.seller_phone}</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2 pt-1">
              <a 
                href="tel:${actionData.seller_phone}" 
                class="py-2 bg-emerald-500 hover:bg-emerald-400 text-dark-950 font-bold rounded-xl text-center text-xs flex items-center justify-center space-x-1.5 shadow-md"
              >
                <i data-lucide="phone" class="w-3.5 h-3.5"></i>
                <span>Call Seller Now</span>
              </a>
              <a 
                href="mailto:${actionData.seller_email}?subject=Direct Buyer Inquiry for ${encodeURIComponent(actionData.property_title)}" 
                class="py-2 bg-dark-850 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold rounded-xl text-center text-xs flex items-center justify-center space-x-1.5"
              >
                <i data-lucide="mail" class="w-3.5 h-3.5"></i>
                <span>Email Broker</span>
              </a>
            </div>
          </div>
        `;
      } else if (intent === 'run_valuation' && actionData.property_id) {
        const topP = recs[0] || {};
        const estVal = Math.round((topP.price || 2000000) * 1.04 / 5000) * 5000;
        const grossYield = topP.price && topP.est_rent ? ((topP.est_rent * 12 / topP.price) * 100).toFixed(2) : "5.80";

        actionBoxHtml = `
          <div class="p-4 rounded-2xl bg-gradient-to-br from-dark-900 to-slate-900 border border-gold-500/40 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-[10px] uppercase font-bold text-gold-400 flex items-center space-x-1.5">
                <i data-lucide="trending-up" class="w-3.5 h-3.5"></i>
                <span>Apex Automated Valuation (AVM)</span>
              </span>
              <span class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[9px] font-bold">92% Comp Confidence</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="p-2.5 rounded-xl bg-dark-850 border border-slate-800">
                <span class="text-[9px] uppercase font-bold text-slate-400 block">Estimated Fair Value</span>
                <span class="text-base font-extrabold text-white">$${estVal.toLocaleString()}</span>
              </div>
              <div class="p-2.5 rounded-xl bg-dark-850 border border-slate-800">
                <span class="text-[9px] uppercase font-bold text-slate-400 block">Est. Gross Yield</span>
                <span class="text-base font-extrabold text-emerald-400">${grossYield}%</span>
              </div>
            </div>
            <button onclick="openApexForProperty(${actionData.property_id})" class="w-full py-2 bg-gradient-to-r from-gold-500 to-amber-600 text-dark-950 font-bold rounded-xl text-xs hover:brightness-110 shadow-md">
              Open Full Apex Valuation & ROI Model
            </button>
          </div>
        `;
      } else if (intent === 'schedule_tour' && actionData.suggested_property_id) {
        const uniqueId = Date.now();
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const defaultDate = tomorrow.toISOString().split('T')[0];

        actionBoxHtml = `
          <div id="inChatTourCard-${uniqueId}" class="p-4 rounded-2xl bg-gradient-to-br from-dark-900 to-slate-900 border border-blue-500/40 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-[10px] uppercase font-bold text-blue-400 flex items-center space-x-1.5">
                <i data-lucide="calendar" class="w-3.5 h-3.5"></i>
                <span>Atlas Autonomous Concierge Booking</span>
              </span>
              <span class="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 text-[9px] font-bold">Slot Available</span>
            </div>
            <p class="text-[11px] text-slate-200 font-semibold">${actionData.suggested_property_title}</p>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div>
                <label class="text-[9px] uppercase font-bold text-slate-400 block mb-0.5">Date</label>
                <input type="date" id="inChatDate-${uniqueId}" value="${defaultDate}" class="w-full bg-dark-850 border border-slate-700 rounded-lg px-2 py-1.5 text-slate-200 text-xs">
              </div>
              <div>
                <label class="text-[9px] uppercase font-bold text-slate-400 block mb-0.5">Time Slot</label>
                <select id="inChatTime-${uniqueId}" class="w-full bg-dark-850 border border-slate-700 rounded-lg px-2 py-1.5 text-slate-200 text-xs">
                  <option value="10:00 AM">10:00 AM</option>
                  <option value="02:00 PM" selected>02:00 PM</option>
                  <option value="04:30 PM">04:30 PM</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <input type="text" id="inChatName-${uniqueId}" placeholder="Your Name" value="Private Buyer" class="bg-dark-850 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 text-xs">
              <input type="email" id="inChatEmail-${uniqueId}" placeholder="Your Email" value="buyer@estatesphere.com" class="bg-dark-850 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 text-xs">
            </div>
            <button onclick="submitInChatTour(${actionData.suggested_property_id}, '${uniqueId}')" class="w-full py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold rounded-xl text-xs hover:brightness-110 shadow-md flex items-center justify-center space-x-1.5">
              <i data-lucide="check" class="w-3.5 h-3.5"></i>
              <span>Confirm Reservation & Generate .ICS</span>
            </button>
          </div>
        `;
      }

      // Dynamic Cognitive Reasoning Follow-up Chips
      const followUpChipsHtml = recs.length > 0 && intent !== 'consultation' ? `
        <div class="pt-2 border-t border-slate-800/60 space-y-1.5">
          <span class="text-[9px] uppercase tracking-wider text-slate-400 font-bold block">💡 Deep Dive Reasoning Questions:</span>
          <div class="flex flex-wrap gap-1.5">
            <button onclick="sendAriaQuery('Compare the carrying costs and HOA fees between these options')" class="px-2.5 py-1 rounded-lg bg-dark-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-gold-400 text-[10px] transition-all">
              "Compare HOA carrying costs"
            </button>
            <button onclick="sendAriaQuery('What are the lifestyle trade-offs for family life and schools?')" class="px-2.5 py-1 rounded-lg bg-dark-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-gold-400 text-[10px] transition-all">
              "Evaluate for family & schools"
            </button>
            <button onclick="sendAriaQuery('Which property delivers the highest rental yield and cap rate?')" class="px-2.5 py-1 rounded-lg bg-dark-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-emerald-400 text-[10px] transition-all">
              "Highest rental yield & cap rate"
            </button>
          </div>
        </div>
      ` : '';

      // Aria Response Bubble
      let html = `
        <div class="flex items-start space-x-3 bg-dark-850/90 border border-slate-800 rounded-2xl p-3.5">
          <div class="w-7 h-7 rounded-lg bg-gold-500/20 text-gold-400 flex items-center justify-center shrink-0 mt-0.5">
            <i data-lucide="bot" class="w-4 h-4"></i>
          </div>
          <div class="space-y-3 flex-1">
            <div class="flex items-center justify-between">
              <span class="font-bold text-gold-400 flex items-center space-x-1.5">
                <span>Aria Cognitive Advisor</span>
                <span class="text-[9px] px-1.5 py-0.2 rounded ${aiStatus.classes} font-bold">${aiStatus.label}</span>
              </span>
              <span class="text-[10px] text-slate-400 font-medium">
                ${recs.length > 0 ? `${recs.length} Analyzed Asset${recs.length === 1 ? '' : 's'}` : 'Private Client Advisory'}
              </span>
            </div>
            <div class="text-slate-200 leading-relaxed text-xs">${formattedText}</div>

            ${actionBoxHtml}

            <!-- Curated Recommendations Cards with Seller Calling (Rendered only when specific properties match) -->
            ${recs.length > 0 ? `
              <div class="space-y-2 pt-1">
                ${recs.slice(0, 3).map(p => `
                  <div class="p-2.5 rounded-xl bg-dark-900 border border-slate-800 flex items-center space-x-3 hover:border-gold-500/50 transition-all">
                    <img src="${p.image_url}" class="w-14 h-14 object-cover rounded-lg shrink-0 cursor-pointer" onclick="openPropertyModal(${p.id})">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center justify-between cursor-pointer" onclick="openPropertyModal(${p.id})">
                        <span class="font-bold text-white truncate text-xs">${p.title}</span>
                        <span class="text-gold-400 font-bold text-xs shrink-0 ml-1">$${p.price.toLocaleString()}</span>
                      </div>
                      <p class="text-[10px] text-slate-400 truncate">${p.address}, ${p.city}</p>
                      <div class="flex items-center justify-between mt-1 pt-1 border-t border-slate-800/60 text-[10px]">
                        <span class="text-slate-400 truncate">Agent: ${p.agent_name}</span>
                        <div class="flex items-center space-x-1.5 shrink-0">
                          <a href="tel:${p.agent_phone}" class="text-emerald-400 font-bold hover:underline flex items-center space-x-0.5">
                            <i data-lucide="phone" class="w-2.5 h-2.5"></i>
                            <span>Call</span>
                          </a>
                          <span>•</span>
                          <a href="https://api.whatsapp.com/send?phone=${p.agent_phone.replace(/[^0-9]/g, '')}&text=${encodeURIComponent('Hi ' + p.agent_name + ', I am inquiring about ' + p.title + ' on EstateSphere.')}" target="_blank" class="text-emerald-400 hover:underline">WhatsApp</a>
                          <span>•</span>
                          <button onclick="copyPropertyLink(${p.id})" class="text-gold-400 hover:underline">Share Link</button>
                        </div>
                      </div>
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : ''}

            ${ragCitationsHtml}
            ${followUpChipsHtml}

            <!-- Action Button to Apply to Main View -->
            ${recs.length > 0 ? `
              <button onclick="applyAriaResults(${JSON.stringify(recs).replace(/"/g, '&quot;')})" class="w-full py-2 bg-gradient-to-r from-gold-500 to-amber-600 text-dark-950 font-bold rounded-xl text-xs hover:brightness-110 shadow-md">
                Filter Explorer & Map to These Matches
              </button>
            ` : ''}
          </div>
        </div>
      `;

      transcript.innerHTML += html;
      transcript.scrollTop = transcript.scrollHeight;
      lucide.createIcons();
    }
  } catch (err) {
    document.getElementById(typingId)?.remove();
    console.error(err);
    transcript.innerHTML += `
      <div class="bg-rose-500/10 border border-rose-500/30 text-rose-200 rounded-xl p-3 text-xs">
        I couldn't reach Aria. Check that the EstateSphere server is running, then try again.
      </div>
    `;
    transcript.scrollTop = transcript.scrollHeight;
  }
}

async function submitInChatTour(propertyId, uniqueId) {
  const card = document.getElementById(`inChatTourCard-${uniqueId}`);
  const date = document.getElementById(`inChatDate-${uniqueId}`)?.value;
  const time = document.getElementById(`inChatTime-${uniqueId}`)?.value;
  const name = document.getElementById(`inChatName-${uniqueId}`)?.value || 'Private Buyer';
  const email = document.getElementById(`inChatEmail-${uniqueId}`)?.value || 'buyer@estatesphere.com';

  if (!date || !time) {
    alert('Please choose a valid tour date and time.');
    return;
  }

  try {
    const res = await fetch('/api/agents/schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        property_id: propertyId,
        buyer_name: name,
        buyer_email: email,
        buyer_phone: '+1 (555) 019-4820',
        tour_date: date,
        tour_time: time,
        tour_type: 'In-Person VIP Guided Tour',
        notes: 'Booked directly via Aria Autonomous RAG Chatbot'
      })
    });
    const data = await res.json();

    if (data.success && card) {
      const d = data.result.details;
      card.className = 'p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/40 text-slate-100 space-y-2.5 text-xs';
      card.innerHTML = `
        <div class="flex items-center space-x-2 text-emerald-400 font-bold">
          <i data-lucide="check-circle" class="w-4 h-4"></i>
          <span>Tour Confirmed by Atlas Concierge!</span>
        </div>
        <p class="text-slate-300 text-[11px]">
          Reserved for <strong>${date} at ${time}</strong> with listing agent <strong>${d.listing_agent.name}</strong> (${d.listing_agent.phone}).
        </p>
        <div class="pt-1 flex items-center space-x-2">
          <a href="${d.calendar_download_url}" download="tour.ics" class="px-3 py-1.5 bg-emerald-500 text-dark-950 font-bold rounded-lg text-xs hover:bg-emerald-400 flex items-center space-x-1">
            <i data-lucide="download" class="w-3 h-3"></i>
            <span>Download .ICS Calendar Event</span>
          </a>
        </div>
      `;
      refreshToursCount();
      lucide.createIcons();
    } else {
      alert(data.error || 'Could not confirm tour.');
    }
  } catch (err) {
    console.error(err);
  }
}

// Voice Recognition Integration
function startVoiceInput(inputId, btnId, autoSend = false) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  const btn = document.getElementById(btnId);
  if (btn) {
    btn.classList.add('text-rose-500', 'animate-pulse');
  }

  recognition.onresult = (event) => {
    const transcriptText = event.results[0][0].transcript;
    const inputEl = document.getElementById(inputId);
    if (inputEl) {
      inputEl.value = transcriptText;
      if (autoSend) {
        handleAriaSend();
      } else {
        handleSearchSubmit();
      }
    }
  };

  recognition.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    if (btn) {
      btn.classList.remove('text-rose-500', 'animate-pulse');
    }
  };

  recognition.onend = () => {
    if (btn) {
      btn.classList.remove('text-rose-500', 'animate-pulse');
    }
  };

  recognition.start();
}

function applyAriaResults(recommendations) {
  if (!recommendations || recommendations.length === 0) return;
  state.filteredProperties = recommendations;
  renderPropertiesGrid(recommendations);
  updateMapPins(recommendations);
  document.getElementById('activeCriteriaNote').textContent = `(Showing ${recommendations.length} Aria AI Curated Listings)`;
  toggleAgentDrawer(false);
}

// --- APEX (AGENT 2: VALUATION & INVESTMENT AVM) ---
function populateAgentPropertySelects(properties) {
  const apexSelect = document.getElementById('apexPropertySelect');
  const atlasSelect = document.getElementById('atlasPropertySelect');

  const options = properties.map(p => `
    <option value="${p.id}">${p.title} - $${p.price.toLocaleString()} (${p.city})</option>
  `).join('');

  if (apexSelect) apexSelect.innerHTML = options;
  if (atlasSelect) atlasSelect.innerHTML = options;
}

function openApexForProperty(propId) {
  toggleAgentDrawer(true);
  switchAgentTab('apex');
  const select = document.getElementById('apexPropertySelect');
  if (select) {
    select.value = propId;
    runApexValuation();
  }
}

function setApexMode(mode) {
  const listedBtn = document.getElementById('apexModeListed');
  const customBtn = document.getElementById('apexModeCustom');
  const listedSec = document.getElementById('apexListedSection');
  const customSec = document.getElementById('apexCustomSection');

  if (mode === 'listed') {
    listedBtn.className = 'flex-1 py-1.5 rounded-lg text-xs font-bold transition-all bg-emerald-500 text-dark-950 shadow-md';
    customBtn.className = 'flex-1 py-1.5 rounded-lg text-xs font-bold transition-all text-slate-400 hover:text-white';
    listedSec.classList.remove('hidden');
    customSec.classList.add('hidden');
    runApexValuation();
  } else {
    customBtn.className = 'flex-1 py-1.5 rounded-lg text-xs font-bold transition-all bg-emerald-500 text-dark-950 shadow-md';
    listedBtn.className = 'flex-1 py-1.5 rounded-lg text-xs font-bold transition-all text-slate-400 hover:text-white';
    customSec.classList.remove('hidden');
    listedSec.classList.add('hidden');
  }
}

async function runCustomApexValuation() {
  const city = document.getElementById('apexCustomCity').value;
  const ptype = document.getElementById('apexCustomType').value;
  const sqft = parseInt(document.getElementById('apexCustomSqft').value) || 2000;
  const beds = parseInt(document.getElementById('apexCustomBeds').value) || 3;
  const baths = parseFloat(document.getElementById('apexCustomBaths').value) || 2.0;
  const price = parseInt(document.getElementById('apexCustomPrice').value) || 2000000;

  const features = [];
  if (document.getElementById('apexFeatView')?.checked) features.push('Panoramic Views');
  if (document.getElementById('apexFeatPool')?.checked) features.push('Private Pool');
  if (document.getElementById('apexFeatElevator')?.checked) features.push('Private Elevator');
  if (document.getElementById('apexFeatSmart')?.checked) features.push('Smart Automation');

  const container = document.getElementById('apexResultsContainer');
  container.innerHTML = `
    <div class="p-8 text-center text-slate-400 space-y-2">
      <i data-lucide="loader" class="w-6 h-6 animate-spin mx-auto text-emerald-400"></i>
      <p class="text-xs">Running AVM model for custom ${beds}B/${baths}B in ${city}...</p>
    </div>
  `;
  lucide.createIcons();

  try {
    const res = await fetch('/api/agents/valuation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        custom_inputs: {
          city: city,
          type: ptype,
          sqft: sqft,
          beds: beds,
          baths: baths,
          price: price,
          features: features
        }
      })
    });
    const data = await res.json();
    if (data.success) {
      renderValuationCard(data.result);
    }
  } catch (err) {
    console.error(err);
  }
}

function renderValuationCard(v) {
  const container = document.getElementById('apexResultsContainer');
  const m = v.investment_metrics;

  container.innerHTML = `
    <div class="p-4 rounded-2xl bg-dark-850 border border-slate-800 space-y-3">
      <div class="flex items-center justify-between">
        <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">${v.property_title}</span>
        <span class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-[10px]">
          ${v.confidence_score}% Confidence
        </span>
      </div>

      <div class="flex items-baseline justify-between pt-1">
        <div>
          <span class="text-[10px] text-slate-400 block">Estimated Fair Market Value</span>
          <span class="text-2xl font-black text-white tracking-tight">$${v.estimated_value.toLocaleString()}</span>
        </div>
        <div class="text-right">
          <span class="text-[10px] text-slate-400 block">Baseline Asking</span>
          <span class="text-sm font-bold text-slate-300">$${v.actual_price.toLocaleString()}</span>
        </div>
      </div>

      <div class="bg-dark-900 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between text-[11px]">
        <span class="text-slate-400">Est. Range:</span>
        <span class="font-bold text-slate-200">$${v.valuation_range.low.toLocaleString()} - $${v.valuation_range.high.toLocaleString()}</span>
      </div>

      <div class="p-3 rounded-xl bg-dark-900 border border-slate-800 space-y-1.5">
        <div class="flex justify-between items-center text-xs">
          <span class="font-bold text-slate-200">Deal Quality Score</span>
          <span class="font-black text-gold-400">${v.deal_score} / 100</span>
        </div>
        <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div class="bg-gradient-to-r from-amber-500 to-emerald-400 h-full rounded-full" style="width: ${v.deal_score}%"></div>
        </div>
        <p class="text-[11px] font-medium text-slate-300 pt-1">${v.verdict}</p>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-2.5">
      <div class="p-3 rounded-xl bg-dark-850 border border-slate-800">
        <span class="text-[10px] uppercase font-bold text-slate-400 block">Est. Gross Yield</span>
        <span class="text-lg font-bold text-emerald-400">${m.gross_rental_yield_pct}%</span>
        <span class="text-[10px] text-slate-500 block">~$${m.est_monthly_rent.toLocaleString()} / mo rent</span>
      </div>
      <div class="p-3 rounded-xl bg-dark-850 border border-slate-800">
        <span class="text-[10px] uppercase font-bold text-slate-400 block">Net Cap Rate</span>
        <span class="text-lg font-bold text-gold-400">${m.cap_rate_pct}%</span>
        <span class="text-[10px] text-slate-500 block">Net NOI: $${m.net_annual_income.toLocaleString()}</span>
      </div>
      <div class="col-span-2 p-3 rounded-xl bg-dark-850 border border-slate-800 flex items-center justify-between">
        <div>
          <span class="text-[10px] uppercase font-bold text-slate-400 block">5-Year Equity Forecast</span>
          <span class="text-xs text-slate-300">Projected Value: $${m.five_year_projected_value.toLocaleString()}</span>
        </div>
        <span class="text-sm font-bold text-emerald-400">+$${m.projected_5yr_equity_gain.toLocaleString()}</span>
      </div>
    </div>

    <div class="p-3.5 rounded-2xl bg-dark-850 border border-slate-800 space-y-1.5">
      <div class="flex items-center space-x-2 text-gold-400 text-xs font-bold">
        <i data-lucide="shield-alert" class="w-4 h-4"></i>
        <span>Apex Agent Negotiation Tip</span>
      </div>
      <p class="text-slate-300 text-[11px] leading-relaxed">
        ${v.negotiation_advice}
      </p>
    </div>

    <div class="p-3 rounded-2xl bg-dark-850 border border-slate-800 space-y-2">
      <span class="text-[10px] uppercase font-bold text-slate-400 block">Recent Verified Comps</span>
      ${v.comparables.map(c => `
        <div class="flex items-center justify-between text-[11px] py-1 border-b border-slate-800/60 last:border-0">
          <span class="text-slate-200 truncate w-44">${c.title}</span>
          <span class="font-bold text-gold-400">$${c.price.toLocaleString()}</span>
          <span class="text-slate-500">$${c.price_per_sqft}/sqft</span>
        </div>
      `).join('')}
    </div>
  `;
  lucide.createIcons();
}

async function runApexValuation() {
  const select = document.getElementById('apexPropertySelect');
  const propId = select?.value;
  if (!propId) return;

  const container = document.getElementById('apexResultsContainer');
  container.innerHTML = `
    <div class="p-8 text-center text-slate-400 space-y-2">
      <i data-lucide="loader" class="w-6 h-6 animate-spin mx-auto text-emerald-400"></i>
      <p class="text-xs">Computing Automated Valuation Model (AVM) comps & yield...</p>
    </div>
  `;
  lucide.createIcons();

  try {
    const res = await fetch('/api/agents/valuation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ property_id: parseInt(propId) })
    });
    const data = await res.json();

    if (data.success) {
      renderValuationCard(data.result);
    }
  } catch (err) {
    console.error(err);
  }
}

// --- ATLAS (AGENT 3: TOUR SCHEDULING CONCIERGE) ---
function openAtlasForProperty(propId) {
  toggleAgentDrawer(true);
  switchAgentTab('atlas');
  const select = document.getElementById('atlasPropertySelect');
  if (select) select.value = propId;
}

function setupDefaultDates() {
  const dateInput = document.getElementById('atlasTourDate');
  if (dateInput) {
    // Tomorrow as default
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.value = tomorrow.toISOString().split('T')[0];
    dateInput.min = new Date().toISOString().split('T')[0];
  }
}

async function submitAtlasTourBooking() {
  const propId = document.getElementById('atlasPropertySelect')?.value;
  const tourDate = document.getElementById('atlasTourDate')?.value;
  const tourTime = document.getElementById('atlasTourTime')?.value;
  const tourType = document.querySelector('input[name="atlasTourType"]:checked')?.value || 'In-Person Guided Tour';
  const buyerName = document.getElementById('atlasBuyerName')?.value.trim();
  const buyerEmail = document.getElementById('atlasBuyerEmail')?.value.trim();
  const buyerPhone = document.getElementById('atlasBuyerPhone')?.value.trim();
  const notes = document.getElementById('atlasNotes')?.value.trim();

  const banner = document.getElementById('atlasResultBanner');

  if (!buyerName || !buyerEmail || !tourDate) {
    banner.className = 'p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs block';
    banner.textContent = 'Please complete your name, email, and choose a valid tour date.';
    return;
  }

  try {
    const res = await fetch('/api/agents/schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        property_id: parseInt(propId),
        buyer_name: buyerName,
        buyer_email: buyerEmail,
        buyer_phone: buyerPhone,
        tour_date: tourDate,
        tour_time: tourTime,
        tour_type: tourType,
        notes: notes
      })
    });
    const data = await res.json();

    if (data.success) {
      const d = data.result.details;
      banner.className = 'p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-slate-100 text-xs block space-y-3';
      banner.innerHTML = `
        <div class="flex items-center space-x-2 text-emerald-400 font-bold">
          <i data-lucide="check-circle-2" class="w-4 h-4"></i>
          <span>${data.result.message}</span>
        </div>
        <div class="space-y-1 text-slate-300 text-[11px]">
          <p><strong>Property:</strong> ${d.property_title}</p>
          <p><strong>Date & Time:</strong> ${d.tour_date} at ${d.tour_time}</p>
          <p><strong>Agent Contact:</strong> ${d.listing_agent.name} (${d.listing_agent.phone})</p>
        </div>
        <a href="${d.calendar_download_url}" download="tour.ics" class="inline-flex items-center space-x-2 px-3 py-2 bg-emerald-500 text-dark-950 font-bold rounded-xl text-xs hover:bg-emerald-400 transition-all">
          <i data-lucide="calendar-plus" class="w-4 h-4"></i>
          <span>Download .ICS Calendar Event</span>
        </a>
      `;
      refreshToursCount();
      lucide.createIcons();
    } else {
      banner.className = 'p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs block';
      banner.textContent = data.error || 'Failed to book tour.';
    }
  } catch (err) {
    console.error(err);
  }
}

// ============================================================================
// 5. PROPERTY DETAIL MODAL & MORTGAGE CALCULATOR
// ============================================================================
async function openPropertyModal(id) {
  const modal = document.getElementById('propertyModal');
  const content = document.getElementById('propertyModalContent');

  content.innerHTML = `
    <div class="py-16 text-center text-slate-400">
      <i data-lucide="loader" class="w-8 h-8 animate-spin mx-auto text-gold-400 mb-2"></i>
      <p class="text-xs">Loading residence architectural portfolio...</p>
    </div>
  `;
  modal.classList.remove('hidden');
  lucide.createIcons();

  try {
    const res = await fetch(`/api/properties/${id}`);
    const data = await res.json();

    if (data.success) {
      const p = data.property;

      content.innerHTML = `
        <!-- Media View Tabs -->
        <div class="space-y-3">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <div class="flex space-x-2 text-xs">
              <button onclick="switchMediaTab('gallery', ${p.id})" id="mediaTabGallery" class="px-3 py-1.5 rounded-lg font-bold bg-gold-500 text-dark-950 transition-all flex items-center space-x-1.5">
                <i data-lucide="image" class="w-3.5 h-3.5"></i>
                <span>Photo Gallery</span>
              </button>
              <button onclick="switchMediaTab('floorplan', ${p.id})" id="mediaTabFloorplan" class="px-3 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white hover:bg-slate-800 transition-all flex items-center space-x-1.5">
                <i data-lucide="layout" class="w-3.5 h-3.5"></i>
                <span>Floor Plan Specs</span>
              </button>
              <button onclick="switchMediaTab('virtual3d', ${p.id})" id="mediaTabVirtual3d" class="px-3 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white hover:bg-slate-800 transition-all flex items-center space-x-1.5">
                <i data-lucide="box" class="w-3.5 h-3.5"></i>
                <span>3D Virtual Walkthrough</span>
              </button>
            </div>
            <button onclick="toggleCompare(${p.id})" class="text-xs text-gold-400 hover:text-gold-300 font-semibold flex items-center space-x-1">
              <i data-lucide="git-compare" class="w-3.5 h-3.5"></i>
              <span>Add to Comparison Tray</span>
            </button>
          </div>

          <!-- Tab 1: Hero Gallery -->
          <div id="mediaContentGallery" class="grid grid-cols-1 md:grid-cols-3 gap-2.5 h-64 md:h-80 rounded-2xl overflow-hidden">
            <div class="md:col-span-2 h-full">
              <img src="${p.gallery[0] || p.image_url}" class="w-full h-full object-cover rounded-xl" alt="${p.title}">
            </div>
            <div class="grid grid-rows-2 gap-2.5 h-full">
              <img src="${p.gallery[1] || p.image_url}" class="w-full h-full object-cover rounded-xl" alt="Interior">
              <img src="${p.gallery[2] || p.image_url}" class="w-full h-full object-cover rounded-xl" alt="Living">
            </div>
          </div>

          <!-- Tab 2: Floor Plan & Room Dimensions -->
          <div id="mediaContentFloorplan" class="hidden p-6 rounded-2xl bg-dark-850 border border-slate-800 space-y-4">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3">
              <div>
                <h4 class="font-bold text-sm text-slate-100">Architectural Space Blueprint & Dimensions</h4>
                <p class="text-[11px] text-slate-400">Total Measured Usable Footprint: ${p.sqft.toLocaleString()} SqFt</p>
              </div>
              <span class="px-2.5 py-1 rounded-full bg-gold-500/10 text-gold-400 font-bold text-xs border border-gold-500/20">CAD Verified</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div class="p-3 rounded-xl bg-dark-900 border border-slate-800">
                <span class="text-[10px] uppercase font-bold text-slate-400 block">Primary Master Suite</span>
                <span class="font-bold text-slate-200">24' x 18' (En-Suite Spa)</span>
              </div>
              <div class="p-3 rounded-xl bg-dark-900 border border-slate-800">
                <span class="text-[10px] uppercase font-bold text-slate-400 block">Great Room / Living</span>
                <span class="font-bold text-slate-200">32' x 22' (14ft Ceilings)</span>
              </div>
              <div class="p-3 rounded-xl bg-dark-900 border border-slate-800">
                <span class="text-[10px] uppercase font-bold text-slate-400 block">Chef's Kitchen</span>
                <span class="font-bold text-slate-200">18' x 14' (Center Island)</span>
              </div>
              <div class="p-3 rounded-xl bg-dark-900 border border-slate-800">
                <span class="text-[10px] uppercase font-bold text-slate-400 block">Outdoor Terrace</span>
                <span class="font-bold text-emerald-400">450 SqFt Private</span>
              </div>
            </div>
            <div class="h-44 rounded-xl border border-dashed border-slate-700 bg-dark-900/60 flex flex-col items-center justify-center text-slate-400 text-xs space-y-1">
              <i data-lucide="compass" class="w-8 h-8 text-gold-400/80 mb-1"></i>
              <span class="font-semibold text-slate-300">CAD Floorplan Vector Model Rendered</span>
              <span class="text-[10px] text-slate-500">North-facing primary orientation with dual sunrise balconies</span>
            </div>
          </div>

          <!-- Tab 3: Simulated 3D Virtual Walkthrough -->
          <div id="mediaContentVirtual3d" class="hidden relative h-64 md:h-80 rounded-2xl overflow-hidden border border-slate-800 bg-dark-950 flex items-center justify-center group">
            <img src="${p.gallery[1] || p.image_url}" class="w-full h-full object-cover opacity-40 blur-[1px] group-hover:scale-105 transition-all duration-700">
            <div class="absolute inset-0 bg-gradient-to-t from-dark-950 via-dark-950/40 to-transparent"></div>
            <div class="absolute text-center space-y-3 z-10 px-4">
              <div class="w-16 h-16 mx-auto rounded-full bg-gold-500/20 border-2 border-gold-400 flex items-center justify-center text-gold-400 shadow-2xl backdrop-blur-md cursor-pointer hover:scale-110 active:scale-95 transition-all">
                <i data-lucide="play" class="w-7 h-7 fill-gold-400 ml-1"></i>
              </div>
              <div>
                <h4 class="font-extrabold text-base text-white">4K Spatial 3D Walkthrough Tour</h4>
                <p class="text-xs text-slate-300">Dollhouse 3D geometry & live walkthrough with listing agent</p>
              </div>
              <button onclick="closePropertyModal(); openAtlasForProperty(${p.id});" class="px-4 py-2 bg-gradient-to-r from-gold-500 to-amber-600 text-dark-950 font-bold rounded-xl text-xs hover:brightness-110 shadow-lg">
                Schedule Guided 4K Live Walkthrough
              </button>
            </div>
          </div>
        </div>

        <!-- Header Section -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
          <div>
            <div class="flex items-center space-x-2 mb-1">
              <span class="px-2.5 py-0.5 rounded-full bg-gold-500/20 text-gold-400 font-bold text-xs uppercase tracking-wider">${p.type}</span>
              <span class="text-xs text-slate-400">Built in ${p.year_built}</span>
            </div>
            <h2 class="text-2xl font-black text-white tracking-tight">${p.title}</h2>
            <p class="text-xs text-slate-400 mt-0.5">${p.address}, ${p.city}, ${p.state} ${p.zip}</p>
          </div>
          <div class="text-left md:text-right">
            <div class="text-3xl font-black text-gold-400">$${p.price.toLocaleString()}</div>
            <div class="text-xs text-slate-400">$${Math.round(p.price / p.sqft).toLocaleString()} / sqft • Est. Rent: $${p.est_rent.toLocaleString()}/mo</div>
          </div>
        </div>

        <!-- Key Metrics Strip -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="p-3.5 rounded-xl bg-dark-850 border border-slate-800">
            <span class="text-[10px] uppercase font-bold text-slate-400 block">Bedrooms / Baths</span>
            <span class="text-sm font-bold text-slate-200">${p.beds} Beds • ${p.baths} Baths</span>
          </div>
          <div class="p-3.5 rounded-xl bg-dark-850 border border-slate-800">
            <span class="text-[10px] uppercase font-bold text-slate-400 block">Total Living Area</span>
            <span class="text-sm font-bold text-slate-200">${p.sqft.toLocaleString()} SqFt</span>
          </div>
          <div class="p-3.5 rounded-xl bg-dark-850 border border-slate-800">
            <span class="text-[10px] uppercase font-bold text-slate-400 block">Monthly Carrying Cost</span>
            <span class="text-sm font-bold text-slate-200">HOA: $${p.hoa_fee} • Tax: $${p.property_tax}</span>
          </div>
          <div class="p-3.5 rounded-xl bg-dark-850 border border-slate-800">
            <span class="text-[10px] uppercase font-bold text-slate-400 block">Neighborhood Scores</span>
            <span class="text-sm font-bold text-emerald-400">School: ${p.school_rating}/10 • Transit: ${p.transit_score}/100</span>
          </div>
        </div>

        <!-- Description -->
        <div class="space-y-2">
          <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider">Residence Overview</h3>
          <p class="text-xs text-slate-300 leading-relaxed">${p.description}</p>
        </div>

        <!-- Amenities Chips -->
        <div class="space-y-2">
          <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider">Luxury Amenities & Features</h3>
          <div class="flex flex-wrap gap-2">
            ${p.features.map(f => `
              <span class="px-3 py-1.5 rounded-xl bg-dark-850 border border-slate-700 text-xs text-slate-200 flex items-center space-x-1.5">
                <i data-lucide="check" class="w-3.5 h-3.5 text-gold-400"></i>
                <span>${f}</span>
              </span>
            `).join('')}
          </div>
        </div>

        <!-- Historical Price Appreciation Chart (Chart.js) -->
        <div class="p-5 rounded-2xl bg-dark-850 border border-slate-800 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-100 flex items-center space-x-2">
              <i data-lucide="trending-up" class="w-4 h-4 text-emerald-400"></i>
              <span>Historical Price Appreciation Trajectory</span>
            </h3>
            <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
              +${calculateAppreciationGain(p.price_history)}% Since Inception
            </span>
          </div>
          <div class="h-44 w-full">
            <canvas id="priceHistoryChart"></canvas>
          </div>
        </div>

        <!-- Interactive Mortgage Calculator & Doughnut Breakdown -->
        <div class="p-5 rounded-2xl bg-dark-850 border border-slate-800 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-100 flex items-center space-x-2">
              <i data-lucide="calculator" class="w-4 h-4 text-gold-400"></i>
              <span>Interactive Monthly Carrying Cost Estimator</span>
            </h3>
            <span id="monthlyPaymentTotal" class="text-lg font-black text-emerald-400">$0 / mo</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-5 items-center">
            <div class="md:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div>
                <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Down Payment (20%)</label>
                <input type="number" id="calcDownPayment" value="${Math.round(p.price * 0.2)}" oninput="recalcMortgage(${p.price}, ${p.hoa_fee}, ${p.property_tax})" class="w-full bg-dark-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100">
              </div>
              <div>
                <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Interest Rate (%)</label>
                <input type="number" step="0.1" id="calcInterestRate" value="6.5" oninput="recalcMortgage(${p.price}, ${p.hoa_fee}, ${p.property_tax})" class="w-full bg-dark-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100">
              </div>
              <div>
                <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Loan Term</label>
                <select id="calcLoanTerm" onchange="recalcMortgage(${p.price}, ${p.hoa_fee}, ${p.property_tax})" class="w-full bg-dark-900 border border-slate-700 rounded-xl px-3 py-2 text-slate-100">
                  <option value="30">30 Years Fixed</option>
                  <option value="15">15 Years Fixed</option>
                </select>
              </div>

              <!-- Payment Breakdown legend -->
              <div class="sm:col-span-3 pt-1 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800">
                <span class="flex items-center space-x-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-gold-400"></span>
                  <span id="legendPI">P&I: $0</span>
                </span>
                <span class="flex items-center space-x-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-blue-400"></span>
                  <span id="legendTax">Taxes: $${p.property_tax}</span>
                </span>
                <span class="flex items-center space-x-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                  <span id="legendHOA">HOA: $${p.hoa_fee}</span>
                </span>
              </div>
            </div>

            <!-- Doughnut Chart Canvas -->
            <div class="h-28 flex items-center justify-center">
              <canvas id="mortgageDonutChart" class="max-h-28"></canvas>
            </div>
          </div>
        </div>

        <!-- Agent Contact Bar & Tour Trigger -->
        <div class="p-5 rounded-2xl bg-gradient-to-r from-dark-950 to-slate-900 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
          <div class="flex items-center space-x-3.5">
            <img src="${p.agent_avatar}" class="w-14 h-14 rounded-full object-cover border-2 border-gold-500 shadow-md">
            <div>
              <span class="text-[10px] uppercase font-bold text-emerald-400 block tracking-wider">Verified Exclusive Listing Representative</span>
              <h4 class="font-bold text-white text-base">${p.agent_name}</h4>
              <p class="text-xs text-slate-300 font-medium">${p.agent_phone} • ${p.agent_email}</p>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
            <a 
              href="tel:${p.agent_phone}" 
              class="flex-1 md:flex-initial px-4 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-dark-950 font-bold text-xs rounded-xl flex items-center justify-center space-x-1.5 shadow-lg shadow-emerald-500/20 active:scale-95 transition-all"
            >
              <i data-lucide="phone-call" class="w-4 h-4"></i>
              <span>Call Seller</span>
            </a>
            <a 
              href="mailto:${p.agent_email}?subject=Private Buyer Inquiry for ${encodeURIComponent(p.title)}" 
              class="px-3.5 py-2.5 bg-dark-850 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold text-xs rounded-xl flex items-center space-x-1.5 transition-all"
            >
              <i data-lucide="mail" class="w-4 h-4"></i>
              <span>Email</span>
            </a>
            <button 
              onclick="copyPropertyLink(${p.id})"
              class="px-3.5 py-2.5 bg-dark-850 hover:bg-slate-800 border border-gold-500/30 text-gold-400 font-semibold text-xs rounded-xl flex items-center space-x-1.5 transition-all"
              title="Copy direct shareable live link"
            >
              <i data-lucide="share-2" class="w-4 h-4"></i>
              <span>Live Link</span>
            </button>
            <button 
              onclick="closePropertyModal(); openAtlasForProperty(${p.id});" 
              class="flex-1 md:flex-initial px-4 py-2.5 bg-gradient-to-r from-gold-500 to-amber-600 text-dark-950 font-bold text-xs rounded-xl hover:brightness-110 shadow-lg shadow-gold-500/20 active:scale-95 transition-all"
            >
              Book Site Tour
            </button>
          </div>
        </div>
      `;

      window.location.hash = `property-${id}`;
      recalcMortgage(p.price, p.hoa_fee, p.property_tax);
      renderPriceHistoryChart(p.price_history);
      lucide.createIcons();
    }
  } catch (err) {
    console.error(err);
  }
}

function calculateAppreciationGain(history) {
  if (!history || history.length < 2) return "0.0";
  const start = history[0].price;
  const end = history[history.length - 1].price;
  const gain = ((end - start) / start) * 100;
  return gain.toFixed(1);
}

function renderPriceHistoryChart(history) {
  const canvas = document.getElementById('priceHistoryChart');
  if (!canvas) return;

  if (state.charts.history) {
    state.charts.history.destroy();
  }

  const labels = history.map(h => h.year);
  const dataPoints = history.map(h => h.price);

  const ctx = canvas.getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 160);
  gradient.addColorStop(0, 'rgba(197, 168, 128, 0.4)');
  gradient.addColorStop(1, 'rgba(197, 168, 128, 0.0)');

  state.charts.history = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Appraisal Value',
        data: dataPoints,
        borderColor: '#c5a880',
        backgroundColor: gradient,
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#c5a880',
        pointBorderColor: '#0b0f17',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#131b26',
          titleColor: '#f1f5f9',
          bodyColor: '#c5a880',
          borderColor: '#27354a',
          borderWidth: 1,
          padding: 8,
          displayColors: false,
          callbacks: {
            label: function(context) {
              return `$${context.parsed.y.toLocaleString()}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8', font: { size: 10 } }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: '#94a3b8',
            font: { size: 10 },
            callback: function(val) {
              return `$${(val / 1000000).toFixed(1)}M`;
            }
          }
        }
      }
    }
  });
}

function switchMediaTab(tab, propId) {
  const tabs = ['gallery', 'floorplan', 'virtual3d'];
  tabs.forEach(t => {
    const btn = document.getElementById(`mediaTab${t.charAt(0).toUpperCase() + t.slice(1)}`);
    const content = document.getElementById(`mediaContent${t.charAt(0).toUpperCase() + t.slice(1)}`);
    if (t === tab) {
      btn.className = 'px-3 py-1.5 rounded-lg font-bold bg-gold-500 text-dark-950 transition-all flex items-center space-x-1.5 shadow-md';
      content.classList.remove('hidden');
    } else {
      btn.className = 'px-3 py-1.5 rounded-lg font-bold text-slate-400 hover:text-white hover:bg-slate-800 transition-all flex items-center space-x-1.5';
      content.classList.add('hidden');
    }
  });
  lucide.createIcons();
}

function recalcMortgage(price, hoa, tax) {
  const downPayment = parseFloat(document.getElementById('calcDownPayment')?.value) || 0;
  const rateAnnual = parseFloat(document.getElementById('calcInterestRate')?.value) || 6.5;
  const termYears = parseInt(document.getElementById('calcLoanTerm')?.value) || 30;

  const principal = Math.max(price - downPayment, 0);
  const monthlyRate = (rateAnnual / 100) / 12;
  const numPayments = termYears * 12;

  let monthlyPI = 0;
  if (monthlyRate > 0) {
    monthlyPI = principal * (monthlyRate * Math.pow(1 + monthlyRate, numPayments)) / (Math.pow(1 + monthlyRate, numPayments) - 1);
  } else {
    monthlyPI = principal / numPayments;
  }

  const monthlyTax = Math.round(tax);
  const monthlyHOA = Math.round(hoa);
  monthlyPI = Math.round(monthlyPI);
  const totalMonthly = monthlyPI + monthlyTax + monthlyHOA;

  const totalEl = document.getElementById('monthlyPaymentTotal');
  if (totalEl) totalEl.textContent = `$${totalMonthly.toLocaleString()} / mo`;

  const legPI = document.getElementById('legendPI');
  if (legPI) legPI.textContent = `P&I: $${monthlyPI.toLocaleString()}`;

  // Update Doughnut Chart
  renderMortgageDoughnutChart(monthlyPI, monthlyTax, monthlyHOA);
}

function renderMortgageDoughnutChart(pi, tax, hoa) {
  const canvas = document.getElementById('mortgageDonutChart');
  if (!canvas) return;

  if (state.charts.mortgage) {
    state.charts.mortgage.destroy();
  }

  const ctx = canvas.getContext('2d');
  state.charts.mortgage = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Principal & Interest', 'Property Taxes', 'HOA Fee'],
      datasets: [{
        data: [pi, tax, hoa],
        backgroundColor: ['#c5a880', '#60a5fa', '#10b981'],
        borderWidth: 2,
        borderColor: '#131b26'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#131b26',
          titleColor: '#f1f5f9',
          bodyColor: '#c5a880',
          borderColor: '#27354a',
          borderWidth: 1,
          padding: 8,
          callbacks: {
            label: function(c) {
              return `${c.label}: $${c.raw.toLocaleString()}/mo`;
            }
          }
        }
      },
      cutout: '68%'
    }
  });
}

function closePropertyModal() {
  document.getElementById('propertyModal').classList.add('hidden');
  history.replaceState(null, null, ' ');
}

// ============================================================================
// 6. COMPARISON MATRIX (SIDE-BY-SIDE TRAY)
// ============================================================================
function toggleCompare(id) {
  const prop = state.properties.find(p => p.id === id);
  if (!prop) return;

  const index = state.compareList.findIndex(p => p.id === id);
  if (index > -1) {
    state.compareList.splice(index, 1);
    showToast('Removed from comparison tray');
  } else {
    if (state.compareList.length >= 3) {
      showToast('You can compare up to 3 properties at a time.', 'error');
      return;
    }
    state.compareList.push(prop);
    showToast('Added to comparison tray');
  }

  updateCompareDock();
  renderPropertiesGrid(state.filteredProperties);
}

function updateCompareDock() {
  const dock = document.getElementById('compareDock');
  const thumbs = document.getElementById('compareThumbnails');

  if (state.compareList.length === 0) {
    dock.classList.add('translate-y-full');
    return;
  }

  dock.classList.remove('translate-y-full');
  thumbs.innerHTML = state.compareList.map(p => `
    <div class="relative group">
      <img src="${p.image_url}" class="w-10 h-10 rounded-lg object-cover border border-gold-500/40" title="${p.title}">
      <button onclick="toggleCompare(${p.id})" class="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-rose-500 text-white flex items-center justify-center text-[9px]">
        ×
      </button>
    </div>
  `).join('');
}

function clearComparison() {
  state.compareList = [];
  updateCompareDock();
  renderPropertiesGrid(state.filteredProperties);
}

function openComparisonModal() {
  if (state.compareList.length === 0) return;
  const modal = document.getElementById('comparisonModal');
  const container = document.getElementById('comparisonTableContainer');

  const props = state.compareList;

  container.innerHTML = `
    <table class="w-full text-left text-xs border-collapse">
      <thead>
        <tr class="border-b border-slate-800">
          <th class="p-3 text-slate-400 font-bold uppercase text-[10px]">Property Metric</th>
          ${props.map(p => `
            <th class="p-3 text-slate-100 font-bold">
              <img src="${p.image_url}" class="w-full h-32 object-cover rounded-xl mb-2">
              <div class="font-bold text-sm text-gold-400">$${p.price.toLocaleString()}</div>
              <div class="truncate text-xs">${p.title}</div>
            </th>
          `).join('')}
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800/60 text-slate-200">
        <tr>
          <td class="p-3 font-semibold text-slate-400">City / Location</td>
          ${props.map(p => `<td class="p-3">${p.city}, ${p.state}</td>`).join('')}
        </tr>
        <tr>
          <td class="p-3 font-semibold text-slate-400">Property Type</td>
          ${props.map(p => `<td class="p-3 font-medium text-gold-400">${p.type}</td>`).join('')}
        </tr>
        <tr>
          <td class="p-3 font-semibold text-slate-400">Price / SqFt</td>
          ${props.map(p => `<td class="p-3">$${Math.round(p.price / p.sqft).toLocaleString()}</td>`).join('')}
        </tr>
        <tr>
          <td class="p-3 font-semibold text-slate-400">Bedrooms & Baths</td>
          ${props.map(p => `<td class="p-3">${p.beds} Beds / ${p.baths} Baths</td>`).join('')}
        </tr>
        <tr>
          <td class="p-3 font-semibold text-slate-400">Square Footage</td>
          ${props.map(p => `<td class="p-3">${p.sqft.toLocaleString()} sqft</td>`).join('')}
        </tr>
        <tr>
          <td class="p-3 font-semibold text-slate-400">HOA + Monthly Taxes</td>
          ${props.map(p => `<td class="p-3">$${(p.hoa_fee + p.property_tax).toLocaleString()} / mo</td>`).join('')}
        </tr>
        <tr>
          <td class="p-3 font-semibold text-slate-400">Est. Rental Yield</td>
          ${props.map(p => `<td class="p-3 text-emerald-400 font-bold">${((p.est_rent * 12 / p.price) * 100).toFixed(2)}%</td>`).join('')}
        </tr>
        <tr>
          <td class="p-3 font-semibold text-slate-400">School Rating</td>
          ${props.map(p => `<td class="p-3">${p.school_rating} / 10</td>`).join('')}
        </tr>
      </tbody>
    </table>
  `;

  modal.classList.remove('hidden');
  lucide.createIcons();
}

function closeComparisonModal() {
  document.getElementById('comparisonModal').classList.add('hidden');
}

// ============================================================================
// 7. FAVORITES & TOURS DRAWER
// ============================================================================
async function toggleFavorite(id, event) {
  if (event) event.stopPropagation();

  try {
    const res = await fetch('/api/favorites/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ property_id: id })
    });
    const data = await res.json();

    if (data.success) {
      // Update local state
      const p = state.properties.find(item => item.id === id);
      if (p) p.is_favorite = data.is_favorite;

      renderPropertiesGrid(state.filteredProperties);
      updateFavsBadge();
    }
  } catch (err) {
    console.error(err);
  }
}

function updateFavsBadge() {
  const favCount = state.properties.filter(p => p.is_favorite).length;
  const badge = document.getElementById('favsBadge');
  if (badge) {
    if (favCount > 0) {
      badge.textContent = favCount;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  }
}

function filterFavorites() {
  const favs = state.properties.filter(p => p.is_favorite);
  if (favs.length === 0) {
    showToast('No saved favorites yet. Click the heart icon to save.', 'error');
    return;
  }
  state.filteredProperties = favs;
  renderPropertiesGrid(favs);
  updateMapPins(favs);
  document.getElementById('activeCriteriaNote').textContent = `(Showing ${favs.length} Saved Favorites)`;
}

async function refreshToursCount() {
  try {
    const res = await fetch('/api/tours');
    const data = await res.json();
    if (data.success) {
      const badge = document.getElementById('toursBadge');
      if (badge) {
        if (data.count > 0) {
          badge.textContent = data.count;
          badge.classList.remove('hidden');
        } else {
          badge.classList.add('hidden');
        }
      }
    }
  } catch (e) {
    console.warn(e);
  }
}

async function openToursDrawer() {
  const drawer = document.getElementById('toursDrawer');
  const list = document.getElementById('toursList');

  list.innerHTML = `<div class="py-12 text-center text-slate-400 text-xs">Loading scheduled visits...</div>`;
  drawer.classList.remove('translate-x-full');

  try {
    const res = await fetch('/api/tours');
    const data = await res.json();

    if (data.success) {
      if (data.tours.length === 0) {
        list.innerHTML = `
          <div class="py-16 text-center text-slate-400 space-y-2">
            <i data-lucide="calendar" class="w-8 h-8 mx-auto text-slate-600"></i>
            <p class="text-xs">No site tours booked yet.</p>
          </div>
        `;
        lucide.createIcons();
        return;
      }

      list.innerHTML = data.tours.map(t => `
        <div class="p-3.5 rounded-2xl bg-dark-850 border border-slate-800 space-y-2">
          <div class="flex items-center justify-between">
            <span class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-[9px]">
              ${t.status}
            </span>
            <span class="text-[10px] text-slate-400">${t.tour_type}</span>
          </div>
          <div class="flex items-center space-x-3">
            <img src="${t.image_url}" class="w-12 h-12 rounded-xl object-cover shrink-0">
            <div class="min-w-0 flex-1">
              <h4 class="font-bold text-white text-xs truncate">${t.property_title}</h4>
              <p class="text-[10px] text-slate-400 truncate">${t.property_address}</p>
            </div>
          </div>
          <div class="p-2 rounded-xl bg-dark-900 border border-slate-800 text-[11px] text-slate-300 flex justify-between">
            <span>📅 ${t.tour_date}</span>
            <span>⏰ ${t.tour_time}</span>
          </div>
          <div class="flex items-center justify-between pt-1">
            <span class="text-[10px] text-slate-400">Agent: ${t.agent_name}</span>
            <a href="/api/tour/ics/${t.id}" download="tour_${t.id}.ics" class="text-gold-400 hover:underline font-bold text-[10px] flex items-center space-x-1">
              <i data-lucide="download" class="w-3 h-3"></i>
              <span>.ICS Calendar</span>
            </a>
          </div>
        </div>
      `).join('');
      lucide.createIcons();
    }
  } catch (err) {
    console.error(err);
  }
}

function closeToursDrawer() {
  document.getElementById('toursDrawer').classList.add('translate-x-full');
}

// Utility Helpers
function formatPriceAbbr(num) {
  if (num >= 1000000) {
    return `$${(num / 1000000).toFixed(num % 1000000 === 0 ? 0 : 2)}M`;
  }
  return `$${Math.round(num / 1000)}k`;
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
