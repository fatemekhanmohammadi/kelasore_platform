// js/components.js - کامپوننت‌های قابل استفاده مجدد

// ===== رندر کارت کلاس =====
export function renderClassCard(cls) {
    const isOwner = cls.is_owner || false;
    const memberCount = cls.member_count || 0;
    const exerciseCount = cls.exercise_count || 0;
    
    return `
        <div class="card p-6 hover:shadow-xl transition-all duration-300">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h3 class="text-lg font-bold text-blue-600 hover:text-blue-800 transition">
                        <a href="class-detail.html?id=${cls.id}">${cls.title}</a>
                    </h3>
                    <p class="text-gray-600 text-sm mt-1 line-clamp-2">${cls.description || 'بدون توضیحات'}</p>
                </div>
                <span class="badge ${cls.is_private ? 'badge-danger' : 'badge-success'}">
                    ${cls.is_private ? '🔒 خصوصی' : '🌍 عمومی'}
                </span>
            </div>
            
            <div class="mt-4 flex items-center justify-between text-sm text-gray-500">
                <div class="flex items-center gap-3">
                    <span><i class="fas fa-user-tie ml-1"></i> ${cls.teacher_name || 'نامشخص'}</span>
                    <span><i class="fas fa-users ml-1"></i> ${memberCount}</span>
                    <span><i class="fas fa-tasks ml-1"></i> ${exerciseCount}</span>
                </div>
                <span class="text-xs ${cls.is_active ? 'text-green-600' : 'text-gray-400'}">
                    ${cls.is_active ? '● فعال' : '● غیرفعال'}
                </span>
            </div>
            
            <div class="mt-4 flex gap-2">
                <a href="class-detail.html?id=${cls.id}" 
                   class="flex-1 bg-blue-500 text-white text-center py-2 rounded-lg hover:bg-blue-600 transition text-sm">
                    ورود به کلاس
                </a>
                ${isOwner ? `
                    <button onclick="editClass(${cls.id})" 
                            class="bg-yellow-500 text-white px-3 py-2 rounded-lg hover:bg-yellow-600 transition text-sm">
                        <i class="fas fa-cog"></i>
                    </button>
                ` : ''}
            </div>
        </div>
    `;
}

// ===== رندر کارت تمرین =====
export function renderExerciseCard(exercise, classId) {
    const statusMap = {
        'not_started': { label: 'شروع نشده', color: 'gray' },
        'ongoing': { label: 'در حال انجام', color: 'green' },
        'submitted': { label: 'ارسال شده', color: 'blue' },
        'graded': { label: 'نمره داده شده', color: 'purple' }
    };
    
    const status = statusMap[exercise.status] || statusMap['not_started'];
    
    return `
        <div class="card p-6 hover:shadow-lg transition-all duration-300">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h4 class="font-bold text-lg">${exercise.title}</h4>
                    <p class="text-gray-600 text-sm mt-1 line-clamp-2">${exercise.description || ''}</p>
                </div>
                <span class="badge badge-${status.color}">${status.label}</span>
            </div>
            
            <div class="mt-4 flex flex-wrap gap-3 text-sm">
                <span class="px-3 py-1 bg-gray-100 rounded-full text-gray-600">
                    <i class="fas fa-star text-yellow-500 ml-1"></i> ${exercise.score || 0} نمره
                </span>
                <span class="px-3 py-1 bg-gray-100 rounded-full text-gray-600">
                    <i class="fas fa-clock ml-1"></i> ${exercise.time_limit || 'بدون محدودیت'}
                </span>
                <span class="px-3 py-1 bg-gray-100 rounded-full text-gray-600">
                    ${exercise.is_group ? '👥 گروهی' : '👤 انفرادی'}
                </span>
                <span class="px-3 py-1 bg-gray-100 rounded-full text-gray-600">
                    <i class="fas fa-upload ml-1"></i> ${exercise.submission_count || 0}
                </span>
            </div>
            
            <div class="mt-4 flex gap-2">
                <a href="exercise-submit.html?class=${classId}&exercise=${exercise.id}" 
                   class="flex-1 bg-blue-500 text-white text-center py-2 rounded-lg hover:bg-blue-600 transition text-sm">
                    <i class="fas fa-pen ml-1"></i> ارسال پاسخ
                </a>
                ${exercise.answer_type === 'code' ? `
                    <button onclick="openJudge(${exercise.id})" 
                            class="bg-purple-500 text-white px-3 py-2 rounded-lg hover:bg-purple-600 transition text-sm">
                        <i class="fas fa-code"></i>
                    </button>
                ` : ''}
                <button onclick="viewSubmissions(${exercise.id})" 
                        class="bg-gray-500 text-white px-3 py-2 rounded-lg hover:bg-gray-600 transition text-sm">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
        </div>
    `;
}

// ===== رندر جدول نمرات =====
export function renderGradeTable(grades, showRubric = false) {
    if (!grades || grades.length === 0) {
        return `
            <div class="text-center py-12 text-gray-400">
                <i class="fas fa-chart-bar text-6xl"></i>
                <p class="mt-4">هنوز نمره‌ای ثبت نشده است</p>
            </div>
        `;
    }
    
    let html = `
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>رتبه</th>
                        <th>دانشجو</th>
                        <th class="text-center">نمره کل</th>
                        ${showRubric ? '<th class="text-center">ریزنمرات</th>' : ''}
                        <th class="text-center">وضعیت</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    grades.forEach((item, index) => {
        const rank = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`;
        const statusClass = item.status === 'عالی' ? 'badge-success' : 
                           item.status === 'خوب' ? 'badge-info' : 
                           item.status === 'متوسط' ? 'badge-warning' : 'badge-danger';
        
        html += `
            <tr class="${item.is_user ? 'bg-blue-50' : ''}">
                <td class="font-bold">${rank}</td>
                <td>
                    <div class="flex items-center">
                        <img src="https://ui-avatars.com/api/?name=${item.student_name}&background=3B82F6&color=fff&size=30" 
                             class="rounded-full w-8 h-8 ml-2">
                        <span>${item.student_name}</span>
                        ${item.is_user ? '<span class="text-xs text-blue-500 mr-2">(شما)</span>' : ''}
                    </div>
                </td>
                <td class="text-center font-bold">${item.total_score || 0}</td>
                ${showRubric ? `
                    <td class="text-center">
                        ${item.rubric ? Object.entries(item.rubric).map(([key, val]) => 
                            `<span class="inline-block bg-gray-100 px-2 py-1 rounded text-xs ml-1">${key}: ${val}</span>`
                        ).join('') : '-'}
                    </td>
                ` : ''}
                <td class="text-center">
                    <span class="badge ${statusClass}">${item.status || 'در حال انجام'}</span>
                </td>
            </tr>
        `;
    });
    
    html += `</tbody></table></div>`;
    return html;
}

// ===== رندر کامنت‌های فروم =====
export function renderForumPost(post, isOwner = false) {
    return `
        <div class="card p-6 hover:shadow-lg transition-all duration-300">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <div class="flex items-center gap-2">
                        <h4 class="font-bold text-blue-600">${post.title}</h4>
                        ${post.is_pinned ? '<span class="badge badge-warning">📌 پین شده</span>' : ''}
                        ${post.reply_count > 0 ? 
                            '<span class="badge badge-success">پاسخ داده شده</span>' : 
                            '<span class="badge badge-warning">بدون پاسخ</span>'
                        }
                    </div>
                    <p class="text-gray-600 mt-2">${post.content}</p>
                </div>
                ${isOwner ? `
                    <div class="flex gap-2">
                        <button onclick="editPost(${post.id})" class="text-yellow-500 hover:text-yellow-700">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="deletePost(${post.id})" class="text-red-500 hover:text-red-700">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                ` : ''}
            </div>
            
            <div class="mt-4 flex items-center justify-between text-sm text-gray-500">
                <div class="flex items-center gap-4">
                    <span><i class="fas fa-user ml-1"></i> ${post.author}</span>
                    <span><i class="fas fa-clock ml-1"></i> ${post.created_at}</span>
                    <span><i class="fas fa-comment ml-1"></i> ${post.reply_count || 0} پاسخ</span>
                </div>
                <button onclick="toggleReplies(${post.id})" 
                        class="text-blue-500 hover:text-blue-700 font-semibold">
                    مشاهده پاسخ‌ها <i class="fas fa-chevron-down"></i>
                </button>
            </div>
            
            <div id="replies-${post.id}" class="mt-4 pt-4 border-t hidden">
                <!-- پاسخ‌ها -->
            </div>
        </div>
    `;
}

// ===== رندر فرم عضویت در کلاس =====
export function renderJoinClassForm() {
    return `
        <form id="joinClassForm" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    <i class="fas fa-qrcode text-blue-500 ml-1"></i>
                    کد کلاس یا شناسه
                </label>
                <input type="text" id="classCode" required 
                       class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                       placeholder="شناسه کلاس را وارد کنید">
            </div>
            
            <div id="passwordField" class="hidden">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    <i class="fas fa-lock text-blue-500 ml-1"></i>
                    رمز عبور کلاس
                </label>
                <input type="password" id="classPassword" 
                       class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                       placeholder="رمز عبور را وارد کنید">
            </div>
            
            <button type="submit" 
                    class="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition">
                <i class="fas fa-user-plus ml-2"></i>
                عضویت در کلاس
            </button>
        </form>
    `;
}