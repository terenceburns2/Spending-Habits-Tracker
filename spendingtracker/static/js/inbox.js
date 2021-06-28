//Initialises datatable for the inbox on page load
$(document).ready(function() {
    $('#inboxTable').DataTable({
          "columns": [
            {"name": "Message", "orderable": true},
            {"name": "Date", "orderable": true},
        ],
        data: formatMessages()
    })
});

// Formats message data so it can be displayed in the datatable
function formatMessages() {
    let formattedData = [];
    for (let i = 0; i < messages_json.length; i++) {
        date = messages_json[i].timestamp.substring(0, 10);
        time = messages_json[i].timestamp.substring(11, 19);
        timestamp = date + " " + time;
        formattedData.push([messages_json[i].content, timestamp]);
    }

    return formattedData;
}