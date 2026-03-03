from .models import Book, Author, BookInstance, Genre
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .forms import LoanBookForm
import datetime


class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


def index(request):
    """View function for home page of site."""
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }
    return render(request, 'catalog/index.html', context=context)


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    template_name = 'catalog/author_list.html'


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/my_books.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(
            status__exact='o'
        ).order_by('due_back')


# --------------------------
# BOOK CRUD (superusers only)
# --------------------------

class BookCreate(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'book_image']
    template_name = 'catalog/book_form.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()

        # for all genres selected - add the genre many-to-many record
        for genre in form.cleaned_data['genre']:
            theGenre = get_object_or_404(Genre, name=genre)
            post.genre.add(theGenre)

        post.save()
        return HttpResponseRedirect(reverse('book_list'))


class BookUpdate(LoginRequiredMixin, SuperuserRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'book_image']
    template_name = 'catalog/book_form.html'

    def form_valid(self, form):
        post = form.save(commit=False)

        # delete the previously stored genres for the book
        for genre in post.genre.all():
            post.genre.remove(genre)

        # for all genres selected on the form - add the genre many-to-many record
        for genre in form.cleaned_data['genre']:
            theGenre = get_object_or_404(Genre, name=genre)
            post.genre.add(theGenre)

        post.save()
        return HttpResponseRedirect(reverse('book_list'))


class BookDelete(LoginRequiredMixin, SuperuserRequiredMixin, DeleteView):
    model = Book
    template_name = 'catalog/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')


# --------------------------
# AUTHOR CRUD
# --------------------------

class AuthorCreate(SuperuserRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'catalog/author_form.html'
    success_url = reverse_lazy('author_list')


class AuthorDelete(SuperuserRequiredMixin, DeleteView):
    model = Author
    template_name = 'catalog/author_confirm_delete.html'
    success_url = reverse_lazy('author_list')


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'author_image']

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        return HttpResponseRedirect(reverse('author_list'))


def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    try:
        author.delete()
        messages.success(
            request,
            (author.first_name + ' ' + author.last_name + " has been deleted")
        )
    except:
        messages.success(
            request,
            (author.first_name + ' ' + author.last_name + ' cannot be deleted. Books exist for this author')
        )
    return redirect('author_list')


# --------------------------
# AVAILABLE BOOKS + LOAN
# --------------------------

class AvailBooksListView(generic.ListView):
    """Generic class-based view listing all books on loan."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_available.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='a').order_by('book__title')


def loan_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = LoanBookForm(request.POST, instance=book_instance)

        if form.is_valid():
            book_instance = form.save()
            book_instance.due_back = datetime.date.today() + datetime.timedelta(weeks=4)
            book_instance.status = 'o'
            book_instance.save()

            return HttpResponseRedirect(reverse('all_available'))
    else:
        form = LoanBookForm(
            instance=book_instance,
            initial={'book_title': book_instance.book.title}
        )

    return render(request, 'catalog/loan_book_librarian.html', {'form': form})
