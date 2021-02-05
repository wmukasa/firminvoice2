function handleInvoice(){
    var button = document.getElementById("feedback-submit");
    const name_from = document.getElementById('name_from').value;
    const address_from = document.getElementById('address_from').value;
    const email_from = document.getElementById('email_from').value;
    const telephone_from = document.getElementById('telephone_from').value;
    const bus_number_from = document.getElementById('bus_number_from').value;

    const name_to = document.getElementById('name_to').value;
    const address_to = document.getElementById('address_to').value;
    const email_to = document.getElementById('email_to').value;
    const telephone_to = document.getElementById('telephone_to').value;

    sessionStorage.setItem("Name",name_from );
    sessionStorage.setItem("Address",address_from );
    sessionStorage.setItem("Email",email_from );
    sessionStorage.setItem("Telephone",telephone_from );
    sessionStorage.setItem("Bussiness_Number",bus_number_from );

    sessionStorage.setItem("Name_to",name_to );
    sessionStorage.setItem("Address_to",address_to );
    sessionStorage.setItem("Email_to",email_to );
    sessionStorage.setItem("Telephone_to",telephone_to );

    var form = document.getElementById("someForm");
    form.submit();

    return;

}
window.addEventListener('load',() => {
	/*
	const params = (new URL(document.location)).searchParams;
	const name = params.get('name');
	const surname = params.get('surname');*/
	
	const name_from = sessionStorage.getItem('NAME_FROM');
    const address_from= sessionStorage.getItem('ADDRESS_FROM');
    const email_from= sessionStorage.getItem('EMAIL_FROM');
    const telephone_from= sessionStorage.getItem('TELEPHONE_FROM');
    const bus_number_from= sessionStorage.getItem('BUS_NUMBER_FROM');
	
	document.getElementById('from-name').innerHTML = name_from;
    document.getElementById('from-address').innerHTML = address_from;
    document.getElementById('from-email').innerHTML = email_from;
    document.getElementById('from-telephone_num').innerHTML = telephone_from;
    document.getElementById('from-business_num').innerHTML = bus_number_from;
})