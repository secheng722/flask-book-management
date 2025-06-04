// 主JavaScript文件
document.addEventListener('DOMContentLoaded', function() {
    // 自动隐藏提示消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        if (alert.classList.contains('alert-success')) {
            setTimeout(function() {
                alert.style.transition = 'opacity 0.5s';
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 500);
            }, 3000);
        }
    });

    // 表单验证增强
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> 处理中...';
                
                // 如果表单验证失败，恢复按钮状态
                setTimeout(function() {
                    if (form.querySelector('.is-invalid')) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || '提交';
                    }
                }, 100);
            }
        });
        
        // 保存原始按钮文本
        const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
        if (submitBtn) {
            submitBtn.setAttribute('data-original-text', submitBtn.value || submitBtn.textContent);
        }
    });

    // 搜索表单实时搜索（防抖）
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // 可以在这里添加实时搜索功能
                console.log('搜索：', searchInput.value);
            }, 500);
        });
    }

    // 确认删除对话框增强
    const deleteLinks = document.querySelectorAll('a[href*="delete_book"]');
    deleteLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 从链接的onclick属性或周围文本中提取图书标题
            const onclickAttr = this.getAttribute('onclick');
            let title = '此项目';
            
            if (onclickAttr) {
                const bookTitleMatch = onclickAttr.match(/《(.+?)》/);
                if (bookTitleMatch) {
                    title = bookTitleMatch[1];
                }
            } else {
                // 如果没有onclick属性，尝试从父元素中查找图书标题
                const cardBody = this.closest('.card-body');
                if (cardBody) {
                    const titleElement = cardBody.querySelector('.card-title, h5, h2');
                    if (titleElement) {
                        title = titleElement.textContent.trim();
                    }
                }
            }
            
            if (confirm(`确定要删除《${title}》吗？此操作无法撤销。`)) {
                window.location.href = this.href;
            }
        });
    });

    // 工具提示初始化
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // ISBN格式化
    const isbnInputs = document.querySelectorAll('input[name="isbn"]');
    isbnInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            // 移除所有非数字和非字母字符，保留X
            this.value = this.value.replace(/[^0-9X]/gi, '').toUpperCase();
        });
    });

    // 年份验证
    const yearInputs = document.querySelectorAll('input[name="publication_year"]');
    yearInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const currentYear = new Date().getFullYear();
            const value = parseInt(this.value);
            
            if (value < 1000 || value > currentYear) {
                this.setCustomValidity(`出版年份应在1000到${currentYear}之间`);
            } else {
                this.setCustomValidity('');
            }
        });
    });
});

// 工具函数
function showLoading(element) {
    element.classList.add('loading');
}

function hideLoading(element) {
    element.classList.remove('loading');
}

// API调用示例函数
async function fetchBookData(bookId) {
    try {
        const response = await fetch(`/api/book/${bookId}`);
        if (!response.ok) {
            throw new Error('网络请求失败');
        }
        return await response.json();
    } catch (error) {
        console.error('获取图书数据失败:', error);
        return null;
    }
}
