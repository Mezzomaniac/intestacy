const famCtAmAct02 = parseInt(constants['fam_ct_am_act_02']);
let spouse = false;
let defacto = false;
let partner = false;
let survivingIssue = false;
let nonSurvivingIssue = false;
let issue = false;
let parents = false;
let survivingSiblings = false;
let nonsurvivingSiblings = false;
let siblings = false;
let grandparents = false;

$(function() {
    init();
});

function init() {
    displayIfFamCtAmAct02();
    bindEventActions();
};

function displayIfFamCtAmAct02() {
    if ( !famCtAmAct02 ) {
        $('.if-fam-ct-am-act-02').hide().removeProp('required');
    };
};

function bindEventActions() {
    displaySubfields();
    updateSpouse();
    updateDefacto();
    updateSurvivingIssue();
    updateNonsurvivingIssue();
    updateParents();
    updateSurvivingSiblings();
    updateNonsurvivingSiblings();
    updateGrandparents();
};

function displaySubfields() {
    $('.relative-number-field').change(function() {
        let n = Number($(this).val());
        let container = $(this).parent().next().children(); 
        let forms = $(container).children('li');
        $(forms).slice(0, n).slideDown(500).find('input.relative-number-field').prop('required', true);
        $(forms).slice(n).slideUp(500).find('input.relative-number-field').prop('required', false);
    });
};

function updateSpouse() {
    $("input[name='spouse_num']").change(function() {
        spouse = Boolean(Number($(this).val()));
        partner = spouse || defacto;
        displayIfSpouse();
        displayIfNoPartner();
        displayParents();
        displaySiblings();
        displayGrandparents();
        displayAuntuncles();
    });
};

function updateDefacto() {
    function _updateDefacto() {
        defactosNum = Number($('#defactos_num').val());
        let lengths = $("input[name$='length']:checked").get().slice(0, defactosNum).map(elem => Number(elem.value));
        let max = Math.max(...lengths);
        defacto = Boolean(defactosNum && max);
        partner = spouse || defacto;
        displayIfNoPartner();
        displayParents();
        displaySiblings();
        displayGrandparents();
        displayAuntuncles();
    };
    $("#defactos_num").change(_updateDefacto);
    $("input[name$='length']").click(_updateDefacto);
};

function updateSurvivingIssue() {
    $('#surviving_issue_num').change(function() {
        survivingIssue = Boolean(Number($('#surviving_issue_num').val()));
        issue = survivingIssue || nonSurvivingIssue;
        displayParents();
        displaySiblings();
        displayGrandparents();
        displayAuntuncles();
    });
};

function updateNonsurvivingIssue() {
    $("#nonsurviving_issue_num, select[id$='-issue_num']").change(function() {
        nonsurvivingIssueNum = Number($('#nonsurviving_issue_num').val());
        let grandchildren = $('#nonsurviving_issue-div').find("select[id$='-issue_num']").get().slice(0, nonsurvivingIssueNum).map(elem => Number(elem.value));
        let max = Math.max(...grandchildren);
        nonSurvivingIssue = Boolean(nonsurvivingIssueNum && max);
        issue = survivingIssue || nonSurvivingIssue;
        displayParents();
        displaySiblings();
        displayGrandparents();
        displayAuntuncles();
    });
};

function updateParents() {
    $('#parents_num').change(function() {
        parents = Boolean(Number($('#parents_num').val()));
        displaySiblings();
        displayGrandparents();
        displayAuntuncles();
    });
};

function updateSurvivingSiblings() {
    $('#surviving_siblings_num').change(function() {
        survivingSiblings = Boolean(Number($('#surviving_siblings_num').val()));
        siblings = survivingSiblings || nonSurvivingSiblings;
        displayGrandparents();
        displayAuntuncles();
    });
};

function updateNonsurvivingSiblings() {
    $("#nonsurviving_siblings_num, select[id$='-siblings_num']").change(function() {
        nonsurvivingSiblingsNum = Number($('#nonsurviving_siblings_num').val());
        let niblings = $('#nonsurviving_siblings-div').find("select[id$='-siblings_num']").get().slice(0, nonsurvivingSiblingsNum).map(elem => Number(elem.value));
        let max = Math.max(...niblings);
        nonSurvivingSiblings = Boolean(nonsurvivingSiblingsNum && max);
        siblings = survivingSiblings || nonSurvivingSiblings;
        displayGrandparents();
        displayAuntuncles();
    });
};

function updateGrandparents() {
    $('#grandparents_num').change(function() {
        grandparents = Boolean(Number($('#grandparents_num').val()));
        displayAuntuncles();
    });
};

function displayIfSpouse() {
    $('.if-spouse').prop('hidden', !spouse);
};

function displayIfNoPartner() {
    $('.if-no-partner').prop('hidden', partner);
};

function displayParents() {
    $('.parents').prop('hidden', issue);
};

function displaySiblings() {
    $('.siblings').prop('hidden', issue);
};

function displayGrandparents() {
    criteria = !(partner || issue || parents || siblings);
    $('.grandparents').prop('hidden', !criteria);
};

function displayAuntuncles() {
    criteria = !(partner || issue || parents || siblings || grandparents);
    $('.auntuncles').prop('hidden', !criteria);
};
