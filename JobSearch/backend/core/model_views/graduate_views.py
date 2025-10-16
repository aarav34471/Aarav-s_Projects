from core.views import *
    
class UpdateGraduateView(UpdateView):
    model = Graduate
    fields = ['status', 'degree', 'recommendation_tags']
    success_url = reverse_lazy('home')
    template_name = 'ready_jobs/graduate/update_graduate.html'

    def form_valid(self, form):
        graduate = form.instance
        
        if len(graduate.tag_scores) < len(graduate.recommendation_tags):
           
            # If the tag_scores list is shorter than the recommendation_tags list, extend it

           for tag in graduate.recommendation_tags[len(graduate.tag_scores):]:
                
                graduate.tag_scores.append(0) # Add new tag with a score of 
        
        graduate.save()
        messages.success(self.request, "Graduate details updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user  # Ensure user is passed to the template
        return context
    
class GraduateDetailView(DetailView):
    model = Graduate
    template_name = "ready_jobs/graduate/view_graduate.html"
    success_url = reverse_lazy('delete_graduate')
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        graduate = self.get_object()
        context['graduate'] = graduate
        
        return context
    

class DeleteGraduateView(DeleteView):
    model = Graduate

    success_url = reverse_lazy('home')

    template_name ="ready_jobs/graduate/delete_graduate.html"


class ApplyJobView(LoginRequiredMixin, View):
    template_name = "ready_jobs/job/apply_to_job.html"

    def get(self, request, pk):
        job = get_object_or_404(Job, id=pk)
        form = ApplicationForm()
        return render(request, self.template_name, {'job': job, 'form': form})

    def post(self, request, pk):
        job = get_object_or_404(Job, id=pk)
        graduate = get_object_or_404(Graduate, user=request.user)
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            # Check if the graduate has already applied for this job
            if JobApplication.objects.filter(graduate=graduate, job=job).exists():
                messages.warning(request, "You have already applied for this job.")
                return redirect('view_job', pk=job.id)

            # Save the application
            application = form.save(commit=False)
            application.graduate = graduate
            application.job = job
            application.save()

            messages.success(request, "You have successfully applied for the job.")
            return redirect('view_job', pk=job.id)

        return render(request, self.template_name, {'job': job, 'form': form})
    
