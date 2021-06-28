//  JSON data
let logs = logs_json;
console.log(logs);

// Global array for the formatted logs
let formattedLogs = [];

// Calls the format function to format the logs and then initialises the datatable
$(document).ready(function() {
    formatLogs();
    $('#auditTable').DataTable({
        data: formattedLogs
    });
});

// Function to format the log data into a 2d array for the datatable
function formatLogs() {
    for (let i = 0; i < logs.length; i++) {
        formattedLogs.push([logs[i].email, logs[i].ip, logs[i].region, logs[i].login]);
    }
}