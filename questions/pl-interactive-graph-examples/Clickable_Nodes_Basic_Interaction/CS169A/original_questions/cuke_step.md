## Cucumber step definitions (10) (from Fall 2019 midterm 1)

Consider the following Cucumber scenario step and the corresponding
step definition, along with the helper method `find_or_create`.


```
Given the movie "Green Book" has the rating "PG-13"
```

Fill in the blanks to complete the step definition, keeping the
following in mind:

* `Movie` is an `ActiveRecord::Base` subclass whose attributes include
`title` (string) and `rating` (string).
* Since the step definition cannot assume that the movie already exists,
you need to fill in the body of the helper method
`find_or_create_by_title` to account for this.
* Reminder/cheatsheet:  if you call ActiveRecord `where`
it returns an enumerable collection.  Calling `empty?` on this
collection tests if it's empty, calling `first` returns its first
element, etc.  If you call ActiveRecord `find_by`, you get
just the first record found whose attributes match, or `nil` if none
do.  Both methods take a hash of attributes and values to match against.


```ruby
def find_or_create_by_title(movie_title)
  # YOUR CODE HERE (remove the following for exam)
  Movie.find_by(title: movie_title) || Movie.create(title: movie_title)
  # END OF YOUR CODE HERE
end

Given /the movie "(.*)" has the rating "(.*)"/ do |title, rating|
  # YOUR CODE HERE (remove for exam)
  find_or_create_by_title(title).update_attributes(:rating => rating)
  # END OF YOUR CODE HERE  
end
```
Rubric: 4 points for `find_or_create_by_title`, 4 points for step def
