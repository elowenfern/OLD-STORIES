document.addEventListener('DOMContentLoaded', function() {
    console.log('Attaching event listener');
    var payButton = document.getElementById('rzp-button1');

    payButton.addEventListener('click', function(event) {
        event.preventDefault();
        console.log("Button clicked");

        var selects = document.querySelector("[name='addressId']").value;

        if (selects === "") {
            swal("Alert", "Address field is needed", "error");
            return false;
        } else {
            console.log("Fetching data from /proceed-to-pay");
            fetch('/proceed-to-pay')
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    var options = {
                        key: 'rzp_test_Tk26wuocHJyU9Z',
                        amount: data.total * 100,
                        currency: 'INR',
                        name: 'OLD STORIES',
                        description: 'Thank you for Placing an order ',
                        image: 'https://static-00.iconduck.com/assets.00/bill-payment-icon-2048x2048-vpew78n5.png',
                        handler: function(responseb) {
                            if (responseb.razorpay_payment_id) {
                                window.location.href = '/razorpay/';
                            }
                        },
                        prefill: {
                            name: '',
                            email: '',
                            contact: ''
                        },
                        notes: {
                            address: 'Razorpay Corporate Office'
                        },
                        theme: {
                            color: '#D19C97'
                        }
                    };

                    var rzp1 = new Razorpay(options);
                    rzp1.open();
                })
                .catch(function(error) {
                    console.error('Error:', error);
                });
        }
    });
});
checkout.js