(function () {
    var knownCodes = window.KNOWN_CODES || [];
    if (!knownCodes.length) return;

    var fieldId    = window.COURSES_FIELD_ID || 'courses-field';
    var searchInput = document.getElementById('course-search');
    var addBtn      = document.getElementById('add-course-btn');
    var listEl      = document.getElementById('autocomplete-list');
    var chipsEl     = document.getElementById('course-chips');
    var courseField = document.getElementById(fieldId);

    if (!searchInput || !addBtn || !listEl || !chipsEl || !courseField) return;

    var selected = [];

    function syncField() {
        courseField.value = selected.join(', ');
    }

    function renderChips() {
        chipsEl.innerHTML = '';
        selected.forEach(function (code) {
            var chip = document.createElement('span');
            chip.className = 'chip';
            chip.textContent = code;

            var rm = document.createElement('button');
            rm.type = 'button';
            rm.className = 'chip-remove';
            rm.textContent = '×';
            rm.setAttribute('aria-label', 'Remove ' + code);
            rm.addEventListener('click', function () {
                selected = selected.filter(function (c) { return c !== code; });
                renderChips();
                syncField();
            });

            chip.appendChild(rm);
            chipsEl.appendChild(chip);
        });
    }

    function addCourse(code) {
        code = code.trim().toUpperCase();
        if (!code || selected.includes(code)) return;
        selected.push(code);
        renderChips();
        syncField();
        searchInput.value = '';
        listEl.hidden = true;
    }

    function showSuggestions(query) {
        listEl.innerHTML = '';
        if (!query) { listEl.hidden = true; return; }
        var q = query.toUpperCase();
        var matches = knownCodes.filter(function (c) {
            return c.toUpperCase().includes(q);
        }).slice(0, 10);
        if (!matches.length) { listEl.hidden = true; return; }
        matches.forEach(function (code) {
            var item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.textContent = code;
            item.addEventListener('mousedown', function (e) {
                e.preventDefault();
                addCourse(code);
            });
            listEl.appendChild(item);
        });
        listEl.hidden = false;
    }

    searchInput.addEventListener('input', function () {
        showSuggestions(this.value);
    });

    searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            var first = listEl.querySelector('.autocomplete-item');
            addCourse(first ? first.textContent : searchInput.value);
        } else if (e.key === 'Escape') {
            listEl.hidden = true;
        }
    });

    searchInput.addEventListener('blur', function () {
        setTimeout(function () { listEl.hidden = true; }, 150);
    });

    addBtn.addEventListener('click', function () {
        addCourse(searchInput.value);
    });

    // Seed chips from whatever is already in the textarea on load
    if (courseField.value.trim()) {
        courseField.value
            .split(/[,\n]/)
            .map(function (c) { return c.trim().toUpperCase(); })
            .filter(Boolean)
            .forEach(function (c) {
                if (!selected.includes(c)) selected.push(c);
            });
        renderChips();
    }

    // Keep chips in sync when user types directly in the textarea
    courseField.addEventListener('input', function () {
        selected = this.value
            .split(/[,\n]/)
            .map(function (c) { return c.trim().toUpperCase(); })
            .filter(function (c, i, a) { return c && a.indexOf(c) === i; });
        renderChips();
    });
})();
