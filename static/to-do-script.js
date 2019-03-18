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
            <td><button class="btn btn-outline-danger btn-sm" onclick="removeItem('${data.id}')">Delete</button></td
            </tr>`;
        let list = document.querySelector(".todo-list")
        list.innerHTML += html;
      });

    }
  }
