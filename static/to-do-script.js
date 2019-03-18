  function addItem(e) {
    // if enter key is pressed on the form input, add new item
    if (e.which == 13 || e.keyCode == 13) {
      let time = document.querySelector('.time');
      let task = document.querySelector('.task');
      let assignee = document.querySelector('.assignee');
      let overdue = document.querySelector('.overdue');
      let comment = document.querySelector('.comment');
      fetch('/add-todo', {
        method: 'post',
        body: JSON.stringify({
          time: time.value,
          task: task.value,
          assignee: assignee.value,
          overdue: overdue.value,
          comment: comment.value,
          completed: 0
        })
      }).then(function(response) {
        time.value = "";
        task.value = ""
        assignee.value = ""
        overdue.value = ""
        comment.value = ""
        return response.json();
      }).then(function(data) {
        console.log(JSON.stringify(data));
        let html = `
            <tr class="contained-table" id="row-${data.id}">
            <td>${data.time}</td>
            <td>${data.task}</td>
            <td>${data.assignee}</td>
            <td>${data.overdue}</td>
            <td>${data.comment}</td>
            <td>${data.day}</td>
            <td><button type="button" class="btn btn-outline-warning btn-sm" onclick="editItem('${data.id}')">Edit Task</button></td>
            <td><button class="btn btn-outline-danger btn-sm" onclick="removeItem('${data.id}')">Delete</button></td
            </tr>`;
        let list = document.querySelector(".todo-list")
        list.innerHTML += html;
      });

    }
  }

  // function that reads all items from db
  function readItems() {
    fetch('/get_all_tasks')
      .then(function(response) {
        return response.json();
      })
      .then(function(itemsList) {
        displayAllItems(itemsList)
      });
  }

  // adds the items to the innerHTML
  function displayAllItems(itemsList) {
    for (var i = 0; i < itemsList.length; i++) {
      //<td><button class="btn btn-outline-primary btn-sm" type="checkbox" onclick="toggleComplete(this)"
      //data-completed="${itemsList[i]['completed']}" data-id="${itemsList[i]['id']}">Select</button></td>
        let html = `
        <tr class="taable" id="row-${itemsList[i]['id']}">
        <td>${itemsList[i]['time']}</td>
        <td>${itemsList[i]['task']}</td>
        <td>${itemsList[i]['assignee']}</td>
        <td>${itemsList[i]['overdue']}</td>
        <td>${itemsList[i]['comment']}</td>
        <td>${itemsList[i]['day']}</td>

          <td><button type="button" class="btn btn-outline-warning btn-sm">Edit Task</button></td>
          <td><button class="btn btn-outline-danger btn-sm" onclick="removeItem('${itemsList[i]['id']}')">Delete</button></td>


        </tr>
        `
      let list = document.querySelector(".todo-list")
      list.innerHTML += html;
    }
  }

  // function that makes API call to remove an item
  function removeItem(id) {
    fetch(`/remove-todo/${id}`)
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      let item = document.querySelector(`#row-${data.id}`);
        item.parentNode.removeChild(item);
    })
  }

  function editItem(id) {
    fetch(`/edit-todo/${id}`)
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      let item = document.querySelector(`#row-${data.id}`);
        item.parentNode.appendChild(item);
    })
  }



  function readUsers() {
    console.log('reading users')
    fetch('/get_all_users')
      .then(function(response) {
        return response.json();
      })
      .then(function(itemsList) {
        displayAllItems(itemsList)
      });
  }
