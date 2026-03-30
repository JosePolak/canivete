document.addEventListener('DOMContentLoaded', () => {
    const btnInverter = document.getElementById('btn-inverter');
    const selOrigem = document.getElementById('moeda_origem');
    const selDestino = document.getElementById('moeda_destino');
    const inputValor = document.getElementById('valor');
    const form = document.getElementById('form-conversor');

    if (btnInverter && selOrigem && selDestino) {
        btnInverter.addEventListener('click', () => {
            // Troca os valores entre os dois seletores
            const temp = selOrigem.value;
            selOrigem.value = selDestino.value;
            selDestino.value = temp;

            // Se tiver valor, calcula automático
            if (inputValor.value && parseFloat(inputValor.value) > 0) {
                form.submit();
            }
        });
    }
});