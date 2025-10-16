from core.views import *


  
class UpdateEmployerView(UpdateView):
    model = Employer
    fields = "__all__"
    success_url = reverse_lazy('view_employer')
    template_name = 'ready_jobs/employer/update_employer.html'

    def form_valid(self, form):
        messages.success(self.request, "Employer details updated successfully")
        return super().form_valid(form)


class EmployerDetailView(DetailView):
    model = Employer
    template_name = "ready_jobs/employer/view_employer.html"
    success_url = reverse_lazy('delete_employer')

    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        graduate = self.get_object()
        context['graduate'] = graduate
        
        return context
    
class DeleteEmployerView(DeleteView):
    model = Employer

    success_url = reverse_lazy('home')

    template_name ="ready_jobs/graduate/delete_graduate.html"


class EmployerJobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "ready_jobs/job/view_employer_jobs.html"

    def get_queryset(self):
        return Job.objects.filter(company=self.request.user.employer)  # Filter jobs by the logged-in employer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employer'] = self.request.user.employer

        return context
    
class ManageApplicationsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = JobApplication
    template_name = "ready_jobs/employer/view_applicants.html"
    context_object_name = "applications"

    def get_queryset(self):
        job = get_object_or_404(Job, id=self.kwargs['job_id'])
        return JobApplication.objects.filter(job=job)

    def test_func(self):
        job = get_object_or_404(Job, id=self.kwargs['job_id'])
        return self.request.user == job.company.user  # Ensure the employer owns the job

class UpdateApplicationStatusView(LoginRequiredMixin, View):
    def post(self, request, application_id):
        application = get_object_or_404(JobApplication, id=application_id)
        if request.user != application.job.company.user:
            raise PermissionDenied

        status = request.POST.get('status')
        if status in dict(JobApplication.APPLICATION_STATUS):
            application.status = status
            application.save()
            messages.success(request, "Application status updated successfully.")
        else:
            messages.error(request, "Invalid status.")

        return redirect('view_applicant', application_id=application.id)