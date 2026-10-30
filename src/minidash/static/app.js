/* MiniDash customer page. Plain JavaScript, no frameworks, no build step.
 *
 * Pages (chosen by the part of the URL after #):
 *   #/            restaurant list and recent orders
 *   #/r/<id>      one restaurant's menu
 *   #/order/<id>  an order and its live status
 * The cart is a slide-in drawer. Everything talks to the API with api().
 * Text is always added as plain text (never as HTML), so names and
 * addresses typed by people can never be run as code.
 */
"use strict";

// ---------- small helpers ----------

const app = document.getElementById("app");

/** Build a DOM element: el("div", {class: "x", onclick: fn}, "text", otherElement). */
function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value == null || value === false) continue;
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat(Infinity)) { // lists inside lists are fine
    if (child != null && child !== false) node.append(child);
  }
  return node;
}

const money = (cents) => "$" + (cents / 100).toFixed(2);
const pad = (n) => String(n).padStart(2, "0");
const MINUTE = 60 * 1000;

/** The value a <input type="datetime-local"> expects, in the visitor's own time. */
function toLocalInput(date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

/** A friendly date and time in the visitor's own time zone. */
function when(date) {
  return date.toLocaleString([], { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

/** Call the API. Always returns {ok, status, data}; never throws on an HTTP error. */
async function api(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  let data = null;
  try { data = await response.json(); } catch (e) { /* no JSON body */ }
  return { ok: response.ok, status: response.status, data };
}

/** The message to show a customer for a failed call. */
function errorText(result) {
  const data = result.data;
  if (data && data.message) return data.message; // our own {code, message} errors
  if (data && typeof data.detail === "string") return data.detail;
  if (data && Array.isArray(data.detail)) return "Please check your details and try again.";
  return "Something went wrong. Please try again.";
}

let toastTimer = null;
function toast(text) {
  const box = document.getElementById("toast");
  box.textContent = text;
  box.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => box.classList.remove("show"), 3200);
}

// ---------- restaurants: look and hours ----------

const LOOK = {
  Italian: { emoji: "🍕", colors: ["#ffe5d6", "#ffb89a"] },
  Japanese: { emoji: "🍣", colors: ["#ffe0e6", "#ffa9bb"] },
  Mexican: { emoji: "🌮", colors: ["#fff3c4", "#ffd966"] },
  Indian: { emoji: "🍛", colors: ["#ffe9c9", "#ffbf6b"] },
  American: { emoji: "🍔", colors: ["#e3ecff", "#a9c2ff"] },
};
const lookOf = (cuisine) => LOOK[cuisine] || { emoji: "🍽️", colors: ["#eee", "#ccc"] };

function tile(restaurant, className) {
  const look = lookOf(restaurant.cuisine);
  const node = el("div", { class: className }, look.emoji);
  node.style.background = `linear-gradient(135deg, ${look.colors[0]}, ${look.colors[1]})`;
  return node;
}

const minutesOf = (hhmm) => { const [h, m] = hhmm.split(":").map(Number); return h * 60 + m; };

/** The server reads opening hours as UTC, so "open now" is worked out in UTC too. */
function isOpenNow(restaurant) {
  const now = new Date();
  const minutes = now.getUTCHours() * 60 + now.getUTCMinutes();
  return minutesOf(restaurant.opens_at) <= minutes && minutes <= minutesOf(restaurant.closes_at);
}

/** "11:00-22:00 UTC (7:00 AM-6:00 PM your time today)". */
function hoursText(restaurant) {
  const local = (hhmm) => {
    const d = new Date();
    d.setUTCHours(...hhmm.split(":").map(Number), 0, 0);
    return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  };
  return `${restaurant.opens_at}–${restaurant.closes_at} UTC (${local(restaurant.opens_at)}–${local(restaurant.closes_at)} your time)`;
}

let restaurantsCache = null;
async function getRestaurants() {
  if (!restaurantsCache) {
    const result = await api("/restaurants");
    restaurantsCache = result.ok ? result.data : [];
  }
  return restaurantsCache;
}

// ---------- recent orders (kept in this browser only) ----------

const HISTORY_KEY = "minidash.orders";
function savedOrderIds() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; } catch (e) { return []; }
}
function rememberOrder(id) {
  const ids = [id, ...savedOrderIds().filter((x) => x !== id)].slice(0, 6);
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify(ids)); } catch (e) { /* storage unavailable */ }
}

// ---------- cart ----------

const cart = { restaurant: null, menu: [], quantities: {} }; // quantities: menu item id -> how many
const checkout = { mode: "now", when: "", error: "", busy: false };

const cartCount = () => Object.values(cart.quantities).reduce((a, b) => a + b, 0);
const cartTotal = () => cart.menu.reduce((sum, item) => sum + item.price_cents * (cart.quantities[item.id] || 0), 0);

function changeQuantity(item, delta) {
  const next = Math.max(0, (cart.quantities[item.id] || 0) + delta);
  if (next) cart.quantities[item.id] = next; else delete cart.quantities[item.id];
  checkout.error = "";
  refreshCartUi();
}

let afterCartChange = () => {}; // set by the page that is showing, so its buttons stay in step

function refreshCartUi() {
  document.getElementById("cart-count").textContent = cartCount();
  afterCartChange();
  if (!document.getElementById("cart").hidden) renderCart();
}

const addressInput = document.getElementById("address");
addressInput.value = localStorage.getItem("minidash.address") || "";
addressInput.addEventListener("input", () => {
  try { localStorage.setItem("minidash.address", addressInput.value); } catch (e) { /* ignore */ }
});

function stepper(item) {
  return el("div", { class: "stepper" },
    el("button", { type: "button", "aria-label": `Remove one ${item.name}`, onclick: () => changeQuantity(item, -1) }, "−"),
    el("span", {}, String(cart.quantities[item.id])),
    el("button", { type: "button", "aria-label": `Add one ${item.name}`, onclick: () => changeQuantity(item, +1) }, "+"));
}

function openCart() {
  if (!cart.restaurant) { toast("Pick a restaurant first."); return; }
  if (checkout.mode === "now" && !isOpenNow(cart.restaurant) && !checkout.touched) checkout.mode = "later";
  document.getElementById("cart").hidden = false;
  document.getElementById("scrim").hidden = false;
  renderCart();
}
function closeCart() {
  document.getElementById("cart").hidden = true;
  document.getElementById("scrim").hidden = true;
}
document.getElementById("cart-button").addEventListener("click", openCart);
document.getElementById("scrim").addEventListener("click", closeCart);

function quickTimes() {
  const inHours = (h) => new Date(Date.now() + h * 60 * MINUTE);
  const tomorrowAt = (hour) => { const d = new Date(); d.setDate(d.getDate() + 1); d.setHours(hour, 0, 0, 0); return d; };
  return [["In 1 hour", inHours(1)], ["Tomorrow 12:00", tomorrowAt(12)], ["Tomorrow 18:00", tomorrowAt(18)]];
}

function renderCart() {
  const drawer = document.getElementById("cart");
  const lines = cart.menu.filter((item) => cart.quantities[item.id]);

  const scheduleBox = el("div", {});
  if (checkout.mode === "later") {
    const now = Date.now();
    const picker = el("input", {
      class: "field", type: "datetime-local", value: checkout.when, "aria-label": "Delivery time",
      min: toLocalInput(new Date(now + 45 * MINUTE)), max: toLocalInput(new Date(now + 7 * 24 * 60 * MINUTE)),
      oninput: (e) => { checkout.when = e.target.value; checkout.error = ""; },
    });
    scheduleBox.append(
      el("label", { class: "field-label" }, "Deliver at"),
      picker,
      el("div", { class: "quick" }, quickTimes().map(([label, date]) =>
        el("button", { class: "chip", type: "button", onclick: () => { checkout.when = toLocalInput(date); renderCart(); } }, label))),
      el("p", { class: "hint" }, `Choose a time between 45 minutes and 7 days from now, in your own time zone. ${cart.restaurant.name} is open ${hoursText(cart.restaurant)}. Your order goes to the kitchen 30 minutes before delivery, and you can cancel until then.`));
  }

  const submitLabel = checkout.busy ? "Placing order…"
    : `${checkout.mode === "later" ? "Schedule order" : "Place order"} · ${money(cartTotal())}`;

  drawer.replaceChildren(
    el("div", { class: "drawer-head" },
      el("h2", {}, cart.restaurant.name),
      el("button", { class: "close", type: "button", "aria-label": "Close cart", onclick: closeCart }, "✕")),
    el("div", { class: "drawer-body" },
      lines.length === 0 ? el("p", { class: "empty" }, "Your cart is empty.") : [
        lines.map((item) => el("div", { class: "line" },
          el("div", {}, el("div", { class: "name" }, item.name), el("div", { class: "price" }, money(item.price_cents))),
          stepper(item))),
        el("div", { class: "total-row" }, el("span", {}, "Total"), el("span", {}, money(cartTotal()))),
        el("label", { class: "field-label" }, "Delivery address"),
        el("input", {
          class: "field", type: "text", placeholder: "123 Main St", value: addressInput.value, "aria-label": "Address for this order",
          oninput: (e) => { addressInput.value = e.target.value; addressInput.dispatchEvent(new Event("input")); checkout.error = ""; },
        }),
        el("label", { class: "field-label" }, "When"),
        el("div", { class: "segmented" },
          el("button", { type: "button", class: checkout.mode === "now" ? "active" : "", onclick: () => { checkout.mode = "now"; checkout.touched = true; checkout.error = ""; renderCart(); } }, "Deliver now"),
          el("button", { type: "button", class: checkout.mode === "later" ? "active" : "", onclick: () => { checkout.mode = "later"; checkout.touched = true; checkout.error = ""; renderCart(); } }, "Schedule")),
        scheduleBox,
        checkout.error && el("div", { class: "notice", role: "alert" }, checkout.error),
      ]),
    el("div", { class: "drawer-foot" },
      el("button", { class: "pill green", type: "button", disabled: lines.length === 0 || checkout.busy, onclick: placeOrder }, submitLabel)));
}

async function placeOrder() {
  const address = addressInput.value.trim();
  if (!address) { checkout.error = "Please enter a delivery address."; renderCart(); return; }

  const body = {
    restaurant_id: cart.restaurant.id,
    items: Object.entries(cart.quantities).map(([id, quantity]) => ({ menu_item_id: Number(id), quantity })),
    address,
  };
  if (checkout.mode === "later") {
    if (!checkout.when) { checkout.error = "Please pick a delivery time."; renderCart(); return; }
    // The picker gives the visitor's local time; the API wants a time with an offset.
    body.scheduled_delivery_time = new Date(checkout.when).toISOString();
  }

  checkout.busy = true; checkout.error = ""; renderCart();
  const result = await api("/orders", { method: "POST", body: JSON.stringify(body) });
  checkout.busy = false;
  if (!result.ok) { checkout.error = errorText(result); renderCart(); return; }

  rememberOrder(result.data.id);
  cart.quantities = {};
  checkout.when = "";
  refreshCartUi();
  closeCart();
  location.hash = `#/order/${result.data.id}`;
}

// ---------- pages ----------

let pollTimer = null;
const stopPolling = () => { clearInterval(pollTimer); pollTimer = null; };

async function showHome() {
  afterCartChange = () => {};
  const restaurants = await getRestaurants();
  let cuisine = "All";

  const grid = el("div", { class: "grid" });
  const chips = el("div", { class: "chips" });
  const drawGrid = () => {
    chips.replaceChildren(...["All", ...new Set(restaurants.map((r) => r.cuisine))].map((name) =>
      el("button", { class: "chip" + (name === cuisine ? " active" : ""), type: "button", onclick: () => { cuisine = name; drawGrid(); } }, name)));
    grid.replaceChildren(...restaurants.filter((r) => cuisine === "All" || r.cuisine === cuisine).map((r) =>
      el("a", { class: "card", href: `#/r/${r.id}` },
        tile(r, "tile"),
        el("h3", {}, r.name),
        el("div", { class: "meta" }, `${r.cuisine} · about ${r.avg_prep_minutes} min prep`),
        isOpenNow(r) ? el("span", { class: "badge open" }, "Open now")
                     : el("span", { class: "badge closed" }, "Closed now · schedule for later"))));
  };
  drawGrid();

  const recent = el("div", {});
  app.replaceChildren(
    el("section", { class: "hero" },
      el("h1", {}, "Hungry? Order now or schedule it for later."),
      el("p", {}, "Pick a restaurant, add what you like, and choose a delivery time that suits you.")),
    chips, grid, recent);

  const ids = savedOrderIds();
  if (ids.length) {
    const results = await Promise.all(ids.map((id) => api(`/orders/${id}`)));
    const orders = results.filter((r) => r.ok).map((r) => r.data);
    if (orders.length) {
      recent.append(el("h2", { class: "section-title" }, "Your recent orders"),
        el("div", { class: "grid" }, orders.map((order) => {
          const place = restaurants.find((r) => r.id === order.restaurant_id);
          return el("a", { class: "card", href: `#/order/${order.id}` },
            el("h3", {}, `${place ? place.name : "Order"} · #${order.id}`),
            el("div", { class: "meta" }, `${money(order.total_cents)} · ${order.scheduled_delivery_time ? "for " + when(new Date(order.scheduled_delivery_time)) : "delivered ASAP"}`),
            el("span", { class: "badge" }, STATUS_COPY[order.status].title));
        })));
    }
  }
}

async function showRestaurant(id) {
  const restaurants = await getRestaurants();
  const restaurant = restaurants.find((r) => r.id === id);
  if (!restaurant) { app.replaceChildren(el("p", { class: "empty" }, "We could not find that restaurant."), el("a", { class: "back", href: "#/" }, "← All restaurants")); return; }
  const result = await api(`/restaurants/${id}/menu`);
  const menu = result.ok ? result.data : [];

  if (cart.restaurant && cart.restaurant.id !== id && cartCount() > 0) toast(`Your ${cart.restaurant.name} cart was cleared. One restaurant per order.`);
  if (!cart.restaurant || cart.restaurant.id !== id) { cart.quantities = {}; }
  cart.restaurant = restaurant;
  cart.menu = menu;
  refreshCartUi();

  const controls = new Map(); // menu item id -> the element holding its Add button or stepper
  const drawControl = (item) => controls.get(item.id).replaceChildren(
    cart.quantities[item.id] ? stepper(item) : el("button", { class: "add-btn", type: "button", "aria-label": `Add ${item.name}`, onclick: () => changeQuantity(item, +1) }, "+"));

  const bar = el("button", { class: "cart-bar", type: "button", onclick: openCart });
  const drawBar = () => {
    bar.hidden = cartCount() === 0;
    bar.replaceChildren(el("span", {}, `View cart · ${cartCount()} item${cartCount() === 1 ? "" : "s"}`), el("span", {}, money(cartTotal())));
  };
  afterCartChange = () => { menu.forEach(drawControl); drawBar(); };

  app.replaceChildren(
    el("a", { class: "back", href: "#/" }, "← All restaurants"),
    el("div", { class: "r-head" },
      tile(restaurant, "tile"),
      el("div", {},
        el("h1", {}, restaurant.name),
        el("div", { class: "meta" }, `${restaurant.cuisine} · about ${restaurant.avg_prep_minutes} min prep`),
        el("div", { class: "meta" }, `Open ${hoursText(restaurant)}`),
        isOpenNow(restaurant) ? el("span", { class: "badge open" }, "Open now") : el("span", { class: "badge closed" }, "Closed now · you can still schedule an order"))),
    el("div", { class: "menu" }, menu.map((item) => {
      const slot = el("div", {});
      controls.set(item.id, slot);
      return el("div", { class: "menu-row" },
        el("div", {}, el("h3", {}, item.name), el("div", { class: "price" }, money(item.price_cents))), slot);
    })),
    bar);
  afterCartChange();
}

// ---------- the order page ----------

const STATUS_COPY = {
  SCHEDULED: { title: "Scheduled", text: "We will send it to the restaurant 30 minutes before delivery." },
  PLACED: { title: "Order sent to the restaurant", text: "The kitchen has your order." },
  PREPARING: { title: "Being prepared", text: "The restaurant is making your food." },
  READY: { title: "Ready for pickup", text: "A driver is on the way to collect it." },
  PICKED_UP: { title: "On the way", text: "Your food is out for delivery." },
  DELIVERED: { title: "Delivered", text: "Enjoy your meal!" },
  CANCELLED: { title: "Cancelled", text: "This order was cancelled and was not sent to the restaurant." },
};
const PROGRESS = ["PLACED", "PREPARING", "READY", "PICKED_UP", "DELIVERED"];
const FINAL = ["DELIVERED", "CANCELLED"];

async function showOrder(id) {
  afterCartChange = () => {};
  const restaurants = await getRestaurants();
  let confirming = false;
  let message = "";

  const draw = (order) => {
    const place = restaurants.find((r) => r.id === order.restaurant_id);
    const copy = STATUS_COPY[order.status];
    const scheduledFor = order.scheduled_delivery_time ? new Date(order.scheduled_delivery_time) : null;
    const reached = order.status === "SCHEDULED" ? -1 : PROGRESS.indexOf(order.status);
    const cssClass = order.status === "SCHEDULED" ? "scheduled" : order.status === "CANCELLED" ? "cancelled" : order.status === "DELIVERED" ? "delivered" : "";

    const cancelArea = order.status !== "SCHEDULED" ? null : confirming
      ? el("div", { class: "actions" },
          el("button", { class: "pill dark", type: "button", onclick: cancelOrder }, "Yes, cancel the order"),
          el("button", { class: "pill ghost", type: "button", onclick: () => { confirming = false; draw(order); } }, "Keep it"))
      : el("div", { class: "actions" },
          el("button", { class: "pill ghost danger-text", type: "button", onclick: () => { confirming = true; message = ""; draw(order); } }, "Cancel order"));

    app.replaceChildren(el("div", { class: "order" },
      el("a", { class: "back", href: "#/" }, "← All restaurants"),
      el("div", { class: "status-card " + cssClass },
        el("p", {}, `${place ? place.name : "Order"} · #${order.id}`),
        el("h1", {}, copy.title),
        el("p", {}, copy.text),
        order.status !== "CANCELLED" && el("div", {},
          el("div", { class: "steps" }, PROGRESS.map((_, i) => el("div", { class: "step" + (i <= reached ? " done" : "") }))),
          el("div", { class: "step-labels" }, el("span", {}, "Sent"), el("span", {}, "Delivered")))),
      el("div", { class: "panel" },
        el("h2", {}, "Delivery"),
        el("div", { class: "kv" }, el("span", {}, "When"), el("span", {}, scheduledFor ? when(scheduledFor) : "As soon as possible")),
        scheduledFor && order.status === "SCHEDULED" && el("div", { class: "kv" }, el("span", {}, "Sent to the kitchen"), el("span", {}, when(new Date(scheduledFor.getTime() - 30 * MINUTE)))),
        el("div", { class: "kv" }, el("span", {}, "Address"), el("span", {}, order.address))),
      el("div", { class: "panel" },
        el("h2", {}, "Your order"),
        order.items.map((line) => el("div", { class: "kv" }, el("span", {}, `${line.quantity} × ${line.name}`), el("span", {}, money(line.quantity * line.unit_price_cents)))),
        el("div", { class: "kv" }, el("span", {}, "Total"), el("span", {}, money(order.total_cents)))),
      message && el("div", { class: "notice", role: "alert" }, message),
      cancelArea));
  };

  async function load() {
    const result = await api(`/orders/${id}`);
    if (!result.ok) { stopPolling(); app.replaceChildren(el("p", { class: "empty" }, "We could not find that order."), el("a", { class: "back", href: "#/" }, "← All restaurants")); return null; }
    return result.data;
  }

  async function cancelOrder() {
    const result = await api(`/orders/${id}/cancel`, { method: "POST" });
    confirming = false;
    if (result.ok) { toast("Order cancelled."); message = ""; draw(result.data); stopPolling(); return; }
    message = errorText(result); // for example: it was already released to the restaurant
    const latest = await load();
    if (latest) draw(latest);
  }

  const first = await load();
  if (!first) return;
  draw(first);
  if (!FINAL.includes(first.status)) {
    // Check again every few seconds so a release or a status change shows up by itself.
    pollTimer = setInterval(async () => {
      if (confirming) return;
      const latest = await load();
      if (!latest) return;
      draw(latest);
      if (FINAL.includes(latest.status)) stopPolling();
    }, 3000);
  }
}

// ---------- routing ----------

async function route() {
  stopPolling();
  closeCart();
  const [page, value] = (location.hash || "#/").slice(2).split("/");
  window.scrollTo(0, 0);
  if (page === "r") await showRestaurant(Number(value));
  else if (page === "order") await showOrder(Number(value));
  else await showHome();
}
window.addEventListener("hashchange", route);
route();
