let toastTimeout; // Variabel kosong untuk simpan timer

function showToast(message, type = 'info', duration = 3000) {
  const toast = document.getElementById('toast-notification');
  const toastMessage = document.getElementById('toast-message');

  if (!toast || !toastMessage) return; // Elemen tidak ditemukan

  clearTimeout(toastTimeout); // Toast lama belum hilang, batalkan timer

  // Set message
  toastMessage.textContent = message;

  // Reset tampilan toast
  toast.className = 'fixed top-5 right-5 w-full max-w-xs p-4 rounded-lg shadow-lg z-[100] opacity-0 translate-x-full transition-all duration-300 ease-in-out';
  toastMessage.className = 'ms-3 text-sm font-normal flex-grow';

  // Tipe toast
  if (type === 'success') {
    toast.classList.add('bg-white', 'text-[#06005E]', 'border', 'border-[#06005E]');
  } else if (type === 'error') {
    toast.classList.add('bg-red-50', 'text-red-800', 'border', 'border-red-200');
  } else { 
    toast.classList.add('bg-white', 'text-gray-900', 'border', 'border-gray-200');
  }

  // Show toast
  toast.classList.remove('opacity-0', 'translate-x-full'); 
  toast.classList.add('opacity-100', 'translate-x-0'); 

  // Timer baru untuk sembunyiin
  toastTimeout = setTimeout(() => {
    hideToast();
  }, duration);
}

function hideToast() {
  const toast = document.getElementById('toast-notification');
  if (!toast) return;
  toast.classList.remove('opacity-100', 'translate-x-0');
  toast.classList.add('opacity-0', 'translate-x-full');
}