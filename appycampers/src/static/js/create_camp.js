(function () {
  const steps = Array.from(document.querySelectorAll('[data-step]'));
  const indicators = Array.from(document.querySelectorAll('[data-indicator]'));
  const prevButton = document.getElementById('prev-button');
  const nextButton = document.getElementById('next-button');
  const submitButton = document.getElementById('submit-button');
  const detailsForm = document.getElementById('details-form');

  let currentStep = 1;

  function updateStep(n) {
    currentStep = Math.min(Math.max(n, 1), steps.length);

    steps.forEach((el) => {
      el.hidden = Number(el.dataset.step) !== currentStep;
    });

    // Updating current step indicator
    indicators.forEach((el) => {
      const active = Number(el.dataset.indicator) === currentStep;
      el.classList.toggle('is-current', active);
    });

    prevButton.hidden = currentStep === 1;
    nextButton.hidden = currentStep === steps.length;
    submitButton.hidden = currentStep !== steps.length;
  }

  prevButton.addEventListener('click', () => updateStep(currentStep - 1));
  nextButton.addEventListener('click', () => {
    if (currentStep === 1 && !detailsForm.reportValidity()) return; // Check validity on step 1
    updateStep(currentStep + 1);
  });

  const stepButtons = document.querySelectorAll('[data-step-button]');
  for (const button of stepButtons) {
    button.addEventListener('click', function () {
      const step = Number(button.dataset.stepButton);
      if (currentStep === 1 && step > 1 && !detailsForm.reportValidity()) return;
      updateStep(step);
    });
  }

  // Form Object for JSON
  const fields = {
    name: 'camp-name',
    state: 'state',
    city: 'city',
    location: 'location',
    site: 'camp-number',
    type: 'camp-type',
    start: 'start-date',
    end: 'end-date',
    campers: 'expected-campers',
    visibility: 'visibility',
    description: 'camp-description',
  };

  const initialSetup = JSON.parse(document.getElementById('initial-camp-setup').textContent);

  for (const [key, id] of Object.entries(fields)) {
    if (key in initialSetup.details) {
      document.getElementById(id).value = initialSetup.details[key];
    }
  }

  function readDetails() {
    const out = {};
    for (const [key, id] of Object.entries(fields)) {
      out[key] = document.getElementById(id).value;
    }
    return out;
  }

  // Gear Requirements Table
  const gearTable = document.getElementById('gear-table');
  const nameInput = document.getElementById('add-name');
  const qtyInput = document.getElementById('add-quantity');
  let items = [];
  let editingItem = null;

  function makeActionButton(label, onClick) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pure-button';
    btn.textContent = label;
    btn.addEventListener('click', onClick);
    return btn;
  }

  function startEdit(item) {
    editingItem = item;
    render();
    const input = gearTable.querySelector('.edit-name');
    if (input) {
      input.focus();
      input.select();
    }
  }

  function cancelEdit() {
    editingItem = null;
    render();
  }

  function removeItem(item) {
    if (item === editingItem) {
      editingItem = null;
    }
    items = items.filter((other) => other !== item);
    render();
  }

  function makeRow(item) {
    const row = document.createElement('tr');

    row.insertCell().textContent = item.name;
    row.insertCell().textContent = item.qty;

    const actions = row.insertCell();
    actions.className = 'row-actions';
    actions.append(
      makeActionButton('Edit', () => startEdit(item)),
      makeActionButton('Remove', () => removeItem(item))
    );

    return row;
  }

  function makeEditRow(item) {
    const row = document.createElement('tr');

    const nameField = document.createElement('input');
    nameField.type = 'text';
    nameField.className = 'edit-name';
    nameField.value = item.name;

    const qtyField = document.createElement('input');
    qtyField.type = 'number';
    qtyField.className = 'edit-qty';
    qtyField.min = '1';
    qtyField.step = '1';
    qtyField.value = item.qty;

    function save() {
      const name = nameField.value.trim();
      const qty = Number(qtyField.value);
      if (!name) {
        nameField.focus();
        return;
      }
      if (!Number.isInteger(qty) || qty < 1) {
        qtyField.focus();
        return;
      }
      item.name = name;
      item.qty = qty;
      editingItem = null;
      render();
    }

    row.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        save();
      } else if (e.key === 'Escape') {
        cancelEdit();
      }
    });

    row.insertCell().append(nameField);
    row.insertCell().append(qtyField);

    const actions = row.insertCell();
    actions.className = 'row-actions';
    actions.append(
      makeActionButton('Save', save),
      makeActionButton('Cancel', cancelEdit)
    );

    return row;
  }

  function render() {
    const rows = items.map((item) => {
      if (item === editingItem) {
        return makeEditRow(item);
      } else {
        return makeRow(item);
      }
    });
    gearTable.replaceChildren(...rows);
  }

  document.getElementById('add-button').addEventListener('click', () => {
    if (!nameInput.value.trim()) return;
    items.push({ name: nameInput.value.trim(), qty: Number(qtyInput.value) || 1 });
    nameInput.value = '';
    qtyInput.value = '1';
    render();
  });

  // Friends list
  document.getElementById("friend_filter").addEventListener("input", function () {
    const q = this.value.trim().toLowerCase();
    document.querySelectorAll("#friends_table tbody tr[data-search]").forEach(function (row) {
      row.hidden = q !== "" && !row.dataset.search.includes(q);
    });
  });

  function selectedFriendIds() {
    return Array.from(document.querySelectorAll('#friends_table input[name="invitees"]:checked'))
      .map((box) => box.value);
  }

  // Submit
  const errorBox = document.getElementById('form-errors');

  function showErrors(errors) {
    const messages = Object.values(errors);
    errorBox.replaceChildren(...messages.map((msg) => {
      const p = document.createElement('p');
      p.textContent = msg;
      return p;
    }));
    errorBox.hidden = messages.length === 0;

    // Jump back to the step that holds the problem
    const keys = Object.keys(errors);
    if (keys.some((k) => k in fields)) updateStep(1);
    else if (keys.includes('items')) updateStep(2);
    else if (keys.includes('invitees')) updateStep(3);
  }

  submitButton.addEventListener('click', async () => {
    submitButton.disabled = true;
    showErrors({});

    try {
      const res = await fetch('/camps/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...readDetails(), items, invitees: selectedFriendIds() }),
      });
      const data = await res.json().catch(() => ({}));

      if (res.ok && data.redirect) {
        window.location.href = data.redirect;
        return; // Leave the button disabled while navigating
      }
      showErrors(data.errors || { _form: 'Something went wrong. Please try again.' });
    } catch (err) {
      showErrors({ _form: 'Network error. Please check your connection and try again.' });
    }
    submitButton.disabled = false;
  });

  updateStep(1);
  render();
})();