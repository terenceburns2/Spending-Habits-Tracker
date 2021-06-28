//  JSON data
let transaction = transaction_json;
console.log(transaction);
console.log(categories);

// variables like the datatable and chart are defined here so that they are global and can be accessed in helper functions
let datatable;
let dateFrom = $('#dateFrom').val();
let dateTo = $('#dateTo').val();
let chart = constructChart('#piechart');

// Create donut chart when page DOM is ready
$(document).ready(function() {
    updateChart();
});

// Initialises datatable and formats it with a total on page load
$(document).ready(function() {
    $.fn.dataTable.moment("DD-MM-YYYY");
    datatable = $('#transactionTable').DataTable({
        "search": {"regex": true},
        "columns": [
            {"name": "Transaction", "orderable": true},
            {"name": "Date", "orderable": true},
            {"name": "Amount", "orderable": true},
            {"name": "Category", "orderable": false},
            {"orderable": false, "searchable": false}
        ]
        });
    sumTableData();
    formatTransactions();
});

// This function will:
// ---> Remove any previous chart so a new updated chart can be placed into the DOM
// ---> Empty the chart data
// ---> Inputs new chart data depending on the dates selected on the datatable
// ---> Constructs the new chart - builds the SVG
function updateChart() {
    removePreviousChart();
    emptyChartData(chart);
    filterCategoryInsertion();
    displayChart(chart);
}

// Helper function to determine what data to select depending on the date range selected on the datatable
// If no dates are selected then add all transaction data within the donut chart
function filterCategoryInsertion() {
    if (dateFrom === "" && dateTo === "") {
        for (let i = 0; i < transaction_json.length; i ++)
            addCategoryData(chart, transaction_json[i].category, transaction_json[i].amount, null);
    }
    else if (dateFrom !== "" && dateTo !== "") {
        let dateFromObj = new Date(dateFrom);
        let dateToObj = new Date(dateTo);
        for (let i = 0; i < transaction_json.length; i++) {
            let dateObj = new Date(transaction_json[i].timestamp.substring(0, 10));
            if (dateFromObj <= dateObj && dateObj <= dateToObj)
                addCategoryData(chart, transaction_json[i].category, transaction_json[i].amount, null);
        }
    }
}

// Function to remove the transaction location from the transaction description
// This is done by iterating over every row in the table and updating its data
function formatTransactions() {
    datatable.rows().every(function(){
        let data = this.data();
        let newData = [];
        let splitAt = data[0].indexOf(',');

        newData.push(data[0].slice(0, splitAt), data[1], data[2], data[3], data[4]);
        //console.log(newData);
        this.data(newData).draw();

    });
    datatable.draw();
}

// Helper function for the date search to convert dates into a numerical value like '20200504'
function parseDateValue(rawDate) {
    let dateArray = rawDate.split("-");
    let parsedDate = dateArray[0] + dateArray[1] + dateArray[2];
    //console.log(parsedDate);
    return parsedDate;
}

// Function to filter the table by selected categories
// This works by iterating over the checkbox div and generating an array with each selected value
// This is converted into a regex to be searched
function categoryFilter() {
    let selected = [];

    $('#categoryChecks input:checked').each(function () {
        selected.push($(this).attr('value'));
    });

    let searchRegex = selected.join("|");
    datatable.search(searchRegex, true, false).draw();
    sumTableData();
}

// function to validate and then filter the table between the set dates
function datesSearch() {
    let error = false;

    dateFrom = $('#dateFrom').val();
    dateTo = $('#dateTo').val();

    if (dateFrom.length !== 0) {
        $('#dateFrom').removeClass('error');
    } else {
        $('#dateFrom').addClass('error');
        error = true;
    }
    if (dateTo.length !== 0) {
        $('#dateTo').removeClass('error');
    } else {
        $('#dateTo').addClass('error');
        error = true;
    }
    if (error) {
        $('#dateLengthErr').show();
    } else {
        $('#dateLengthErr').hide();
    }

    let dateFromMoment = moment(dateFrom, "YYYY-MM-DD");
    if (dateFromMoment.isAfter(dateTo)) {
        $('#dateFrom').addClass('error');
        $('#dateError').show();
        error = true;
    } else {
        $('#dateError').hide();
    }

    if (error) {
        return;
    }

    // Custom datatable search function to only return rows that are between the 2 dates
    $.fn.dataTableExt.afnFiltering.push(
    function(oSettings, aData, iDataIndex) {
        let dateFrom = parseDateValue($('#dateFrom').val());
        let dateTo = parseDateValue($('#dateTo').val());

        let evalDate = parseDateValue(aData[1]);

        if (evalDate >= dateFrom && evalDate <= dateTo) {
            return true;
        } else {
            return false;
        }
    }
    );

    // Once the table has been searched it must be redrawn to show the filtered results
    datatable.draw();

    sumTableData();
    updateChart();
}

// function to generate the total for the current page of the table
function sumTableData() {
    let total = 0;
    datatable.rows({page:'current'}).every(function (index, element) {
        let data = this.data();
        //console.log(data);
        let entry = parseFloat(data[2].slice(1,data[2].length));
        //console.log(entry);
        total += entry;
    });
    total = total.toFixed(2);
    $('#tableTotal').text("£" + total);
}

// AJAX
function generateTransaction(card_id){
    $.ajax({
        url : '/generate_transaction',
        data : {
            card_id : card_id
        },
        type : "POST",
        complete: function(date) {
            window.location.reload();
        }
    });
}


// card_name Validation:
//  1. Digits or letters (including space ' ')
//  2. Length: 1 ~ 15 characters, can't be empty
//  3. Name cannot be the same as users other cards (This is already implemented
// in the server side, just need a error message like the others.
function validateCardName(card_id) {
    let card_name = $("#cardNameInput").val();
    if (card_name === "") {
        // Display some messages
        return;
    // } else if ( doValidation() ) {
    } else {
        setCardName(card_id, card_name);
    }
}


// Ajax
function setCardName(card_id, card_name) {
    $.ajax({
        url : '/set_card_name',
        data : {
            card_id : card_id,
            card_name : card_name
        },
        type : "POST",
        success: function (data) {
            window.location.reload();
        },
        error: function (msg) {
            if (msg.status === 409){
                // Make it look like a error message like (validation)
                alert("This name is taken by your other card.");
            }
        }
    });
}

// function to get the new category and validate it before posting with ajax
function changeCategory(id) {
    let radio = document.getElementsByClassName(id);
    let newCategory = null;
    for (let i = 0; i < radio.length; i++){
        if (radio[i].checked === true) {
            newCategory = radio[i].value;
            break;
        }
    }
    submitCategory(id, newCategory);
}

// AJAX function to update a category change
function submitCategory(transactionID, newCategory) {
    $.ajax({
        url : '/change_category',
        data : {
            transactionID : transactionID,
            newCategory : newCategory
        },
        type : 'POST',
        complete: function (data) {
            window.location.reload();
        }
    })
}