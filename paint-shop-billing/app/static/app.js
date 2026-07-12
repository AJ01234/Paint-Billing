function formatMoney(value) {
  return `Rs ${Number(value || 0).toFixed(2)}`;
}

async function fetchProducts(query) {
  const response = await fetch(`/api/products/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) {
    return [];
  }
  return response.json();
}

function lineTemplate() {
  const wrapper = document.createElement("div");
  wrapper.className = "invoice-line";
  wrapper.dataset.line = "true";
  wrapper.dataset.basePrice = "";
  wrapper.dataset.gst = "";
  wrapper.dataset.discountMode = "manual";
  wrapper.innerHTML = `
    <div class="search-box">
      <label>Product search
        <input type="text" placeholder="Type brand, size, shade, name" data-product-search autocomplete="off">
      </label>
      <input type="hidden" name="product_id" data-product-id>
      <div class="search-results" data-search-results></div>
    </div>
    <label>Qty<input type="number" step="0.01" name="quantity" value="1" min="0.01" data-qty></label>
    <label>Discount<input type="number" step="0.01" name="discount" value="0" min="0" data-discount></label>
    <label>Price<input type="number" step="0.01" name="unit_price" data-price-input placeholder="Auto"></label>
    <label>GST %<input type="text" data-gst disabled placeholder="Auto"></label>
    <label>Line total<input type="text" data-total disabled placeholder="Auto"></label>
    <button class="button ghost remove-line" type="button" data-remove-line>Remove</button>
  `;
  return wrapper;
}

function syncDiscountFromPrice(line) {
  const qty = Number(line.querySelector("[data-qty]")?.value || 0);
  const priceInput = line.querySelector("[data-price-input]");
  const discountInput = line.querySelector("[data-discount]");
  const basePrice = Number(line.dataset.basePrice || 0);
  const currentPrice = Number(priceInput?.value || 0);
  if (!discountInput || !priceInput || !basePrice) {
    return;
  }
  const derivedDiscount = Math.max((basePrice - currentPrice) * qty, 0);
  discountInput.value = derivedDiscount.toFixed(2);
}

function recalcInvoice() {
  const form = document.querySelector("#invoice-builder");
  if (!form) {
    return;
  }
  const billType = document.querySelector("#bill-type")?.value || "GST";
  const supplyType = document.querySelector("#supply-type")?.value || "INTRA_STATE";
  let subtotal = 0;
  let discount = 0;
  let gst = 0;

  document.querySelectorAll("[data-line]").forEach((line) => {
    const qty = Number(line.querySelector("[data-qty]")?.value || 0);
    const priceInput = line.querySelector("[data-price-input]");
    const discountInput = line.querySelector("[data-discount]");
    if (line.dataset.discountMode === "price_override") {
      syncDiscountFromPrice(line);
    }
    const lineDiscount = Number(discountInput?.value || 0);
    const price = Number(priceInput?.value || 0);
    const gstPercent = billType === "GST" ? Number(line.dataset.gst || 0) : 0;
    const rawSubtotal = qty * price;
    const taxable = Math.max(rawSubtotal - lineDiscount, 0);
    const gstAmount = taxable * gstPercent / 100;
    const total = taxable + gstAmount;

    subtotal += rawSubtotal;
    discount += lineDiscount;
    gst += gstAmount;

    if (priceInput) {
      priceInput.value = price ? Number(price).toFixed(2) : "";
    }
    line.querySelector("[data-gst]").value = `${gstPercent.toFixed(2)}%`;
    line.querySelector("[data-total]").value = total ? formatMoney(total) : "";
  });

  const cgst = billType === "GST" && supplyType !== "INTER_STATE" ? gst / 2 : 0;
  const sgst = billType === "GST" && supplyType !== "INTER_STATE" ? gst / 2 : 0;
  const igst = billType === "GST" && supplyType === "INTER_STATE" ? gst : 0;
  document.querySelector('[data-summary="subtotal"]').textContent = formatMoney(subtotal);
  document.querySelector('[data-summary="discount"]').textContent = formatMoney(discount);
  document.querySelector('[data-summary="cgst"]').textContent = formatMoney(cgst);
  document.querySelector('[data-summary="sgst"]').textContent = formatMoney(sgst);
  document.querySelector('[data-summary="igst"]').textContent = formatMoney(igst);
  document.querySelector('[data-summary="grand_total"]').textContent = formatMoney(subtotal - discount + gst);
}

function bindSearch(line) {
  const input = line.querySelector("[data-product-search]");
  const hiddenId = line.querySelector("[data-product-id]");
  const results = line.querySelector("[data-search-results]");
  if (!input || !hiddenId || !results) {
    return;
  }

  input.addEventListener("input", async () => {
    hiddenId.value = "";
    line.dataset.basePrice = "";
    line.dataset.gst = "";
    line.dataset.discountMode = "manual";
    const priceInput = line.querySelector("[data-price-input]");
    const discountInput = line.querySelector("[data-discount]");
    if (priceInput) {
      priceInput.value = "";
    }
    if (discountInput) {
      discountInput.value = "0";
    }
    recalcInvoice();
    const query = input.value.trim();
    if (query.length < 2) {
      results.innerHTML = "";
      return;
    }
    const products = await fetchProducts(query);
    results.innerHTML = "";
    products.forEach((product) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "search-result-item";
      button.textContent = `${product.display} | Rs ${product.price} | Stock ${product.stock_quantity}`;
      button.addEventListener("click", () => {
        hiddenId.value = product.id;
        input.value = product.display;
        line.dataset.basePrice = product.price;
        line.dataset.gst = product.gst_percent;
        line.dataset.discountMode = "manual";
        const priceInput = line.querySelector("[data-price-input]");
        const discountInput = line.querySelector("[data-discount]");
        if (priceInput) {
          priceInput.value = Number(product.price).toFixed(2);
        }
        if (discountInput) {
          discountInput.value = "0.00";
        }
        results.innerHTML = "";
        recalcInvoice();
      });
      results.appendChild(button);
    });
  });

  document.addEventListener("click", (event) => {
    if (!line.contains(event.target)) {
      results.innerHTML = "";
    }
  });
}

function bindInvoiceBuilder() {
  const container = document.querySelector("[data-lines]");
  if (!container) {
    return;
  }

  container.querySelectorAll("[data-line]").forEach((line) => bindSearch(line));

  document.querySelector("[data-add-line]")?.addEventListener("click", () => {
    const newLine = lineTemplate();
    container.appendChild(newLine);
    bindSearch(newLine);
  });

  container.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }
    if (target.matches("[data-remove-line]")) {
      const lines = container.querySelectorAll("[data-line]");
      if (lines.length > 1) {
        target.closest("[data-line]")?.remove();
        recalcInvoice();
      }
    }
  });

  container.addEventListener("input", recalcInvoice);
  container.addEventListener("input", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }
    const line = target.closest("[data-line]");
    if (!(line instanceof HTMLElement)) {
      return;
    }
    if (target.matches("[data-price-input]")) {
      line.dataset.discountMode = "price_override";
      syncDiscountFromPrice(line);
    }
    if (target.matches("[data-discount]")) {
      line.dataset.discountMode = "manual";
    }
  });
  document.querySelector("#bill-type")?.addEventListener("change", recalcInvoice);
  document.querySelector("#supply-type")?.addEventListener("change", recalcInvoice);
  recalcInvoice();
}

document.addEventListener("DOMContentLoaded", bindInvoiceBuilder);
