from core.views import *

  
class UpdateMentorView(UpdateView):
    
    model = Mentor
    fields = "__all__"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Mentor details updated successfully")
        return super().form_valid(form)

class MentorDetailView(DetailView):
    model = Mentor
    template_name = "ready_jobs/mentor/view_mentor.html"
    success_url = reverse_lazy('delete_mentor')
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        mentor = self.get_object()
        context['mentor'] = mentor
        
        return context
    

class DeleteMentorView(DeleteView):
    model = Mentor

    success_url = reverse_lazy('home')

    template_name ="ready_jobs/mentor/delete_mentor.html"


    