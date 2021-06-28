// Gets the budget value and validates it before sending to an ajax function
function submitMonthlyBudget() {
    let budget = $('#budgetInput').val();
    if (validateBudget(budget)){
        AjaxMonthlyBudget(budget);
    } else {
        alert("Monthly budget is invalid");
    }
}

// Gets the category budget and calls validation functions before sending to an ajax function
function submitCategoryBudget() {
    let category = $('#dropdownMenuButton').text();
    if (category === "Category") {
        alert("Please select a category.");
        return;
    }
    //console.log(category);
    let budget = $('#categoryBudgetInput').val();
    if (validateBudget(budget)){
        AjaxCategoryBudget(category, budget);
    } else {
        alert("Category budget is invalid");
    }
}

// Function to validate budget using a regex
function validateBudget(budget){
    let check = /^\d+(\.{0,1}\d+){0,1}$/;
    return !(budget === "" || !check.test(budget));
}

// Data submission (Ajax)
function AjaxMonthlyBudget(budget){
    $.ajax({
        url : '/set_budget',
        data : {
            budget : budget
        },
        type : "POST",
        success: function (data) {
            window.location.reload();
        },
        error: function (msg) {
            if (msg.status === 403){
                // The budget is the same. i.e. the new budget is same as the old budget
                // Close the modal and do nothing
                console.log(msg);
                $('#budgetModalClose').trigger('click');
            } else {
                console.log(msg);
                alert(msg);
            }
        }
    });
}

// Data submission (Ajax)
function AjaxCategoryBudget(category, budget){
    $.ajax({
        url : '/set_category_budget',
        data : {
            category : category,
            budget : budget
        },
        type : "POST",
        success: function (data) {
            window.location.reload();
        },
        error: function (msg) {
            if (msg.status === 403){
                // The category budget is the same. i.e. the new category budget is same as the old one
                // Close the modal and do nothing
                console.log(msg);
                $('#budgetModalClose').trigger('click');
            } else {
                console.log(msg);
                alert(msg);
            }
        }
    })
}

// Ajax
function removeBudget() {
    $.ajax({
        url : '/remove_budget',
        type : "POST",
        complete: function(data){
            window.location.reload();
            console.log(data);
        }
    })
}

// Ajax
function removeCategoryBudget() {
    let category = $('#dropdownMenuButton').text();
    if (category === "Category"){
        alert("Please select a category.");
        return;
    }
    $.ajax({
        url : '/remove_category_budget',
        type : 'POST',
        data : {
            category : category
        },
        success: function (data) {
            window.location.reload();
            console.log(data);
        },
        error: function (msg) {
            window.location.reload();
            console.log(msg);
        }
    })
}

// Function to add categories to the dropdown menu
$('.dropdown-menu a').click(function(e){
    let categoryButton = $('#dropdownMenuButton');
    categoryButton.text(this.innerHTML);
    console.log(categoryButton.text());
    for (var i = 0; i < categorybudget_json.length; i++){
        if (categoryButton.text() === categorybudget_json[i]['category']){
            console.log(categorybudget_json[i]['category'] + categorybudget_json[i]['budget']);
            $('#categoryBudgetInput').attr('value', categorybudget_json[i]['budget']);
            return;
        } else {
            $('#categoryBudgetInput').attr('value', '');
        }
    }
});

