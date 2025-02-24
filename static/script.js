// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    // 加载动画
    let loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
    }

    // 表单提交前检查
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            let submit = true;
            this.querySelectorAll('[required]').forEach(input => {
                if (!input.value.trim()) {
                    input.style.borderColor = 'red';
                    submit = false;
                }
            });
            if (!submit) {
                e.preventDefault();
            }
        });
    });

    // 导航栏响应式
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const navbarCollapse = document.querySelector('#navbarNav');
            navbarCollapse.classList.toggle('show');
        });
    }

    // 加载中动画
    const loadingElement = document.createElement('div');
    loadingElement.id = 'loading';
    loadingElement.style.position = 'fixed';
    loadingElement.style.top = '0';
    loadingElement.style.left = '0';
    loadingElement.style.right = '0';
    loadingElement.style.bottom = '0';
    loadingElement.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
    loadingElement.style.zIndex = '1000';
    loadingElement.style.display = 'none';
    document.body.appendChild(loadingElement);

    // 显示加载中
    function showLoading() {
        loadingElement.style.display = 'flex';
        loadingElement.innerHTML = `
            <div style="margin: auto; text-align: center;">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
                <p style="margin-top: 10px;">加载中...</p>
            </div>
        `;
    }

    // 隐藏加载中
    function hideLoading() {
        loadingElement.style.display = 'none';
    }

    // 在需要加载的操作前调用 showLoading() 和 hideLoading()
    // 例如：
    document.querySelectorAll('[data-loading]').forEach(element => {
        element.addEventListener('click', function() {
            showLoading();
            // 在异步操作完成后调用 hideLoading()
        });
    });
});
