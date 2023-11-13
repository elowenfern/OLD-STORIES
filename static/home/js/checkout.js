document.addEventListener('DOMContentLoaded', function() {
    var payButton = document.getElementById('rzp-button1');

    payButton.addEventListener('click', function(event) {
        event.preventDefault();

        var addressId = document.querySelector("[name='addressId']").value;
        var shippingId = document.querySelector("[name='shippingId']").value;
        var csrfToken = document.querySelector("[name='csrfmiddlewaretoken']").value;

        if (addressId === "" && shippingId === "")  {
            swal("Alert", "Address field is needed", "error");
            return false;
        } else {
            fetch('/proceed-to-pay',{
                method: 'POST',
                body: JSON.stringify({ addressId: addressId, shippingId: shippingId }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                }
            })
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