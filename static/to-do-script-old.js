// Enable pusher logging for debugging - don't include this in production
Pusher.logToConsole = true;
// wow what a great code
// configure pusher
const pusher = new Pusher('47bd5e95a97b6c383eee', {
  cluster: 'us2', // gotten from Pusher app dashboard
  encrypted: true // optional
});

// subscribe to `todo` public channel, on which we'd be broadcasting events
const channel = pusher.subscribe('todo');

// listen for item-added events, and update todo list once event triggered
channel.bind('item-added', data => {
  appendToList(data);
});

// listen for item-removed events
channel.bind('item-removed', data => {
  let item = document.querySelector(`#row-${data.id}`);
  item.parentNode.removeChild(item);
});

// listen for item-updated events
channel.bind('item-updated', data => {
  let elem = document.querySelector(`#row-${data.id} .toggle`);
  let item = document.querySelector(`#row-${data.id}`);
  item.classList.toggle("completed");
  elem.dataset.completed = data.completed;
  elem.checked = data.completed == 1;
});

// function that makes API call to add an item
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
  })
  .then(resp => {
    // empty form input once a response is received
    time.value = "";
    task.value = ""
    assignee.value = ""
    overdue.value = ""
    comment.value = ""

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
      <td>${itemsList[i]['completed']}</td>
        
        <td><button class="btn btn-outline-danger btn-sm" onclick="removeItem('${itemsList[i]['id']}')">Delete</button></td>


      </tr>
      `
    let list = document.querySelector(".todo-list")
    list.innerHTML += html;
  }
}

// function that makes API call to remove an item
function removeItem(id) {
  fetch(`/remove-todo/${id}`);
}

// function that makes API call to update an item
// toggles the state of the item between complete and
// incomplete states
function toggleComplete(elem) {
  let id = elem.dataset.id,
    completed = (elem.dataset.completed == "1" ? "0" : "1");
  fetch(`/update-todo/${id}`, {
    method: 'post',
    body: JSON.stringify({ completed })
  });
}

// helper function to append new ToDo item to current ToDo list
function appendToList(data) {
  //<td><button class="btn btn-outline-primary btn-sm" type="checkbox" onclick="toggleComplete(this)"
  //data-completed="${data.completed}" data-id="${data.id}">Select</button></td>
  let html = `
      <tr class="contained-table" id="row-${data.id}">
      <td>${data.time}</td>
      <td>${data.task}</td>
      <td>${data.assignee}</td>
      <td>${data.overdue}</td>
      <td>${data.comment}</td>
      <td>${data.completed}</td>
        <td><button class="btn btn-outline-danger btn-sm" onclick="removeItem('${data.id}')">Delete</button></td

      </tr>`;
  let list = document.querySelector(".todo-list")
  list.innerHTML += html;
};
