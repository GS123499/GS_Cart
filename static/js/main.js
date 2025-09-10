// Simple front-end that talks to Flask API
async function fetchProducts(q=''){
const url = q ? '/api/products?q='+encodeURIComponent(q) : '/api/products';
const res = await fetch(url);
return res.json();
}


async function renderProducts(q=''){
const grid = document.getElementById('product-grid');
grid.innerHTML = 'Loading...';
const products = await fetchProducts(q);
grid.innerHTML = '';
products.forEach(p => {
const card = document.createElement('div'); card.className='card';
card.innerHTML = `
<div class="thumb">${p.title.split(' ').map(w=>w[0]).slice(0,2).join('')}</div>
<div class="title">${p.title}</div>
<div class="muted">${p.desc}</div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px">
<div class="price">₹${p.price.toLocaleString()}</div>
<div class="actions">
<button class="btn btn-outline" onclick="addToCart('${p.id}',1)">Add</button>
<button class="btn btn-primary" onclick="buyNow('${p.id}')">Buy</button>
</div>
</div>
`;
grid.appendChild(card);
});
}


async function getCart(){
const res = await fetch('/api/cart');
return res.json();
}


async function updateCartCount(){
const c = await getCart();
