const chartDiv = $('#lineChart');
const currentDate = new Date();
const currentMonth = currentDate.getMonth();
const currentYear = currentDate.getFullYear();

// Calls the function to generate everything on DOM page load
$( document ).ready(function() {
    create();
});

// Selects all with linechart id to obtain an array of current carousel slides (associated with the number of cards the user
// has in their account
const carouselSlides = document.querySelectorAll("#lineChart");

// This is called when the page is ready
    // Loops through the number of cards the user has by using the query selector above.
    // This selector fetches all elements that have the id lineChart
    // This is directly associated with the amount of cards the user has
// Next we iterate through the transactions selecting transactions with the correctly associated card id
// This is added to the data, which the graph will then display using the displayGraph function
// Note: the functions that these call are implemented within linegraph_d3.js
function create() {
    for (let i = 0; i < carouselSlides.length; i++) {
        // Fetch the second attribute (data-name) of the element because this holds the unique identifier
        // which is added when the user submits a card into the database
        let card_id = carouselSlides[i].attributes[2].value;
        // This card_id is then used to fetch the correct element in the DOM to add the SVG
        let graph = constructGraph(card_id, chartDiv.clientWidth, chartDiv.clientHeight);
        // Loop through user transactions and only add data into chart if they are dated with the current month and year
        // This also only fetches and adds transactions to the chart associated with the card_id
        for (let j = 0; j < transaction_json.length; j++) {
            let transactionDate = new Date(transaction_json[j].timestamp);
            if (currentMonth === transactionDate.getMonth() && currentYear === transactionDate.getFullYear()) {
                if (transaction_json[j].card === parseInt(card_id)) {
                    let str = transaction_json[j].timestamp;
                    addDateValue(graph, str.substring(0, 10), transaction_json[j].amount);
                }
            }
        }
        displayGraph(graph);
    }
}

