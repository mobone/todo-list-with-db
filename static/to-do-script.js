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

  function readTodaysItems() {
    create_socket()
    fetch('/get-todays-tasks')
      .then(function(response) {

        return response.json();
      })
      .then(
        function(items_dict) {

          displayTodaysTasks(items_dict['todays_tasks'])

          displayMyTasks(items_dict['my_tasks'])
      });
  }


  // adds the items to the innerHTML
  function displayTodaysTasks(itemsList) {
    for (var i = 0; i < itemsList.length; i++) {
      //<td><button class="btn btn-outline-primary btn-sm" type="checkbox" onclick="toggleComplete(this)"
      //data-completed="${itemsList[i]['completed']}" data-id="${itemsList[i]['id']}">Select</button></td>
      let completed_class = ''
      if (itemsList[i]['completed'] == 1) {
        completed_class = 'class="completed"'
      }
      let html = `
      <tr id="row-${itemsList[i]['id']}" ${completed_class}>
      <td>${itemsList[i]['time']}</td>
      <td>${itemsList[i]['task']}</td>
      <td id="assignee-${itemsList[i]['id']}">${itemsList[i]['assignee']}</td>
      <td>${itemsList[i]['overdue']}</td>
      <td>${itemsList[i]['comment']}</td>
      <td><button class='btn btn-outline-success btn-sm assign-to-me' onclick="assignToMe(${itemsList[i]['id']})" >Assign</button></td>
      </tr>
      `
      let list = document.querySelector(".everyone-todo-list")
      console.log('adding item')
      list.innerHTML += html;


    }
  }

  function displayMyTasks(itemsList) {
    for (var i=0; i < itemsList.length; i++) {

      let completed_class = ''
      if (itemsList[i]['completed'] == 1) {
        completed_class = 'class="completed"'
      }

      let html = `
      <tr id="my-row-${itemsList[i]['id']}" ${completed_class}>
      <td>${itemsList[i]['time']}</td>
      <td>${itemsList[i]['task']}</td>
      <td>${itemsList[i]['assignee']}</td>
      <td>${itemsList[i]['overdue']}</td>
      <td>${itemsList[i]['comment']}</td>
      <td><button class='btn btn-outline-danger btn-sm unassign-to-me' onclick="unassignItem('${itemsList[i]['id']}')">Unassign</button>
      <button class='btn btn-outline-success btn-sm complete' onclick="completeItem('${itemsList[i]['id']}')">Complete</button></td>
      </tr>
      `
      let list = document.querySelector(".me-todo-list")
      console.log('adding item to my todo list')
      list.innerHTML += html;
    }

  }



  function assignToMe(item_id) {

    fetch('/assign-item', {
      method: 'post',
      body: JSON.stringify({
        item_id: item_id
      })
    }).then(function(response) {
      return response.json();
    }).then(function(data) {
      console.log(JSON.stringify(data));
      let completed_class = ''
      if (data['completed'] == 1) {
        completed_class = 'class="completed"'
      }
      let html = `
          <tr id="my-row-${data['id']}" ${completed_class}>
          <td>${data['time']}</td>
          <td>${data['task']}</td>
          <td>${data['assignee']}</td>
          <td>${data['overdue']}</td>
          <td>${data['comment']}</td>
          <td><button class='btn btn-outline-danger btn-sm unassign-to-me' onclick="unassignItem('${data['id']}'), removeAssigneeFromRow('${data['id']}')">Unassign</button>
          <button class='btn btn-outline-success btn-sm complete' onclick="completeItem('${data['id']}')">Complete</button></td>
          </tr>
          `;
      let list = document.querySelector(".me-todo-list")
      list.innerHTML += html;
      addAssigneeToRow(data['id'], data['assignee'])

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
//
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

  function create_socket() {
    console.log('trying to connect')
    var socket = io.connect('http://localhost:5000');

    socket.on('connect', function() {
        console.log("I'm connected")
        socket.emit('my event', {data: 'I\'m connected!'});
    });
    socket.on('completed', function(data) {
      console.log("Got completed message", data)
      color_completed_item(data['id'])

    })
    socket.on('assign', function(data) {
      console.log("Got assign message", data)
      addAssigneeToRow(data['id'], data['assignee'])

    })
    socket.on('unassign', function(data) {
      console.log("Got unassign message", data)
      removeAssigneeFromRow(data['id'])

    })
  }
  //
  function unassignItem(id) {

    fetch(`/unassign-item/${id}`)
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      let item = document.querySelector(`#my-row-${id}`);
        item.parentNode.removeChild(item);
    })
  }

  function color_completed_item(id) {
    let item = document.querySelector(`#row-${id}`);
      item.classList.add('completed')
  }

  function removeAssigneeFromRow(id) {
    let item = document.querySelector(`#assignee-${id}`);
      item.innerHTML = ""
  }

  function addAssigneeToRow(id, assignee) {
    console.log('add assignee to both columns', id, assignee)

    let item = document.querySelector(`#assignee-${id}`);
      item.innerHTML = assignee
  }

  function completeItem(id) {
    console.log('i want to be completed')
    fetch(`/complete-item/${id}`)
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      color_completed_item(id)
    let myItem = document.querySelector(`#my-row-${id}`);
      myItem.classList.add('completed')
    })
  }

// function addAssignee(id) {
//   console.log('I was assigned to both columns')
//   fetch(`/complete-item/${id}`)
//   .then(function(response) {
//     return response.json();
//   })
//   .then(function(data) {
//     color_completed_item(id)
//   let myItem = document.querySelector(`#my-row-${id}`);
//     myItem.classList.add('completed')
//   })



  function readUsers() {
    console.log('reading users')
    fetch('/get_all_users')
      .then(function(response) {
        return response.json();
      })
      .then(function(itemsList) {
        displayAllUsers(itemsList)
      });
  }


  function displayAllUsers(itemsList) {
    for (var i = 0; i < itemsList.length; i++) {
      //<td><button class="btn btn-outline-primary btn-sm" type="checkbox" onclick="toggleComplete(this)"
      //data-completed="${itemsList[i]['completed']}" data-id="${itemsList[i]['id']}">Select</button></td>
        let html = `
        <tr class="taable" id="row-${itemsList[i]['id']}">
        <td>${itemsList[i]['firstname']}</td>
        <td>${itemsList[i]['lastname']}</td>
        <td>${itemsList[i]['username']}</td>

        <td>${itemsList[i]['userType']}</td>


          <td><form>
          <button type="button" class="btn btn-outline-warning btn-sm">Edit User</button>
          </form>
          </td>
          <td>
          <form action="/remove-user" method="post">
          <input hidden name="username" value=${itemsList[i]['username']}>
          <button type="submit" class="btn btn-outline-danger btn-sm">Delete</button>
          </form>
          </td>


        </tr>
        `
      let list = document.querySelector(".addedUsers")
      list.innerHTML += html;
    }
  }
