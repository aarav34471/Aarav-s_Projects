from core.views import *

class ViewAllJobs(ListView):
    model = Job
    template_name = "ready_jobs/job/view_all_jobs.html"
    context_object_name = "jobs"

    def get_queryset(self):
        user = self.request.user

        # If the user is an employer, show only their jobs
        if hasattr(user, 'employer'):
            return Job.objects.filter(company=user.employer)

        # If the user is a graduate, sort jobs based on their tags and scores
        elif hasattr(user, 'graduate'):
            graduate = user.graduate
            
            #Put Tags and scores together using list(zip)
            #Sort the tags by score in descending ordeer
            recommendation_tags = list(zip(graduate.recommendation_tags, graduate.tag_scores))
            sorted_tags_by_score = sorted(recommendation_tags, key=lambda x: x[1], reverse=True)
            jobs = Job.objects.all()
            
            def calculate_job_score(job):
                score = 0
                for tag, tag_score in sorted_tags_by_score:
                    if tag in job.tags:
                        score += tag_score

                return score

            sorted_jobs = sorted(jobs, key=calculate_job_score, reverse=True)
            return sorted_jobs
    
        return Job.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
 
 
class JobDetailView(DetailView):
    model = Job
    template_name = "ready_jobs/job/view_job.html"
    context_object_name = "job"

    def get(self, request, *args, **kwargs):
        job = self.get_object()

        # Check if the user is authenticated and is a graduate
        if request.user.is_authenticated and hasattr(request.user, 'graduate'):
            graduate = request.user.graduate
            # Increment the tag scores for the graduate
            for tag in job.tags:
                graduate.increment_tag_score(tag)

        return super().get(request, *args, **kwargs)
   

class CreateJobView(LoginRequiredMixin, CreateView):
    model = Job
    fields = '__all__'
    success_url = reverse_lazy('home')
    template_name = 'ready_jobs/job/create_job.html'
    
    def form_valid(self, form):
        form.instance.company = self.request.user.employer  # Check that the user is an employer
        messages.success(self.request, "The Job has been created Successfully")
        return super().form_valid(form)

class UpdateJobView(LoginRequiredMixin, UpdateView):
    model = Job
    fields = '__all__'
    success_url = reverse_lazy('home')
    template_name = 'ready_jobs/job/update_job.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()
        context['job'] = job
        return context
    
    def test_func(self):
        job = self.get_object()
        return self.request.user == job.company.user  # Check if the logged-in user is the employer of the job

    def form_valid(self, form):
        messages.success(self.request, "Job details updated successfully")
        return super().form_valid(form)

class DeleteJobView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    success_url = reverse_lazy('home')
    
    def test_func(self):
        job = self.get_object()
        return self.request.user == job.company.user  # Check if the logged-in user is the employer of the job

