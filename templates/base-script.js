//
// Saving this in templates in case we mess stuff up.
// This is backup was created on 03-18-19 after
// adjusting [id] elements on dynamic generation :)
//
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
  let item = document.querySelector(`#${data.id}`);
  item.parentNode.removeChild(item);
});

// listen for item-updated events
channel.bind('item-updated', data => {
  let elem = document.querySelector(`#${data.id} .toggle`);
  let item = document.querySelector(`#${data.id}`);
  item.classList.toggle("completed");
  elem.dataset.completed = data.completed;
  elem.checked = data.completed == 1;
});

// function that makes API call to add an item
function addItem(e) {
// if enter key is pressed on the form input, add new item
if (e.which == 13 || e.keyCode == 13) {
  let item = document.querySelector('.new-todo');
  fetch('/add-todo', {
    method: 'post',
    body: JSON.stringify({
      id: `item-${Date.now()}`,
      value: item.value,
      completed: 0
    })
  })
  .then(resp => {
    // empty form input once a response is received
    item.value = ""
  });
}
}

// function that reads all items from db
function readItems() {
fetch('/get_all_tasks')
.then(resp => {
// empty form input once a response is received

console.log('>>', JSON.stringify(resp))
});

console.log('grandmas alive')
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
let html = `
  <li id="${data.id}">
    <div class="view">
      <input class="toggle" type="checkbox" onclick="toggleComplete(this)"
        data-completed="${data.completed}" data-id="${data.id}">
      <label>${data.value}</label>
      <button class="destroy" onclick="removeItem('${data.id}')">Delete</button>
    </div>
  </li>`;
let list = document.querySelector(".todo-list")
list.innerHTML += html;
};
