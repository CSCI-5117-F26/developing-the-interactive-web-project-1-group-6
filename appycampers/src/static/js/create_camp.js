(function () {
  const steps = Array.from(document.querySelectorAll('[data-step]'));
  const prevButton = document.getElementById('prev-button');
  const nextButton = document.getElementById('next-button');
  const submitButton = document.getElementById('submit-button');

  let currentStep = 1;

  function updateStep(n) {
    currentStep = Math.min(Math.max(n, 1), steps.length);

    steps.forEach((el) => {
      el.hidden = Number(el.dataset.step) !== currentStep;
    });

    prevButton.hidden = currentStep === 1;
    nextButton.hidden = currentStep === steps.length;
    submitButton.hidden = currentStep !== steps.length;
  }

  prevButton.addEventListener('click', () => updateStep(currentStep - 1));
  nextButton.addEventListener('click', () => updateStep(currentStep + 1));
  updateStep(1);

  const gearTable = document.getElementById('gear-table');
  const nameInput = document.getElementById('add-name');
  const qtyInput = document.getElementById('add-quantity');
  const items = [{ name: 'Water Bottles', qty: 1 }];

  function render() {
    gearTable.innerHTML = items.map((item, i) => `
      <tr>
        <td>${item.name}</td>
        <td>${item.qty}</td>
        <td>
          <button type="button" class="pure-button" data-edit="${i}">Edit</button>
          <button type="button" class="pure-button" data-remove="${i}">Remove</button>
        </td>
      </tr>`).join('');
  }

  // Add to internal items array
  document.getElementById('add-button').addEventListener('click', () => {
    if (!nameInput.value.trim()) return;
    items.push({ name: nameInput.value.trim(), qty: Number(qtyInput.value) || 1 });
    nameInput.value = '';
    qtyInput.value = 1;
    render();
  });

  gearTable.addEventListener('click', (e) => {
    const { edit, remove } = e.target.dataset;
    // Object is a remove button, remove the row
    if (remove !== undefined) items.splice(remove, 1);
    // Object is an Edit button, prompt to edit the row, add to internal items array
    if (edit !== undefined) {
      const name = prompt('Item name:', items[edit].name);
      const qty = prompt('Quantity:', items[edit].qty);
      if (name) items[edit] = { name: name.trim(), qty: Number(qty) || 1 };
    }
    render();
  });

  render();
})();