# From S15 quiz 1 unused questions and open-response-exam-questions repo

The MPAA rating system ("G", "PG", etc.) was introduced in 1970, and the PG-13 rating was introduced in 1984.  Enhance the Movie class to check that:

* the rating must be blank if a movie's release date is before 1/1/1970
* the "PG-13" rating is only valid if the movie was released on or after 1/1/1984.

Recall that:
*  `validate :my_validation_method` calls the instance method `my_validation_method` on the model object to be validated

* The `release_date` attribute is a Ruby Time object; these can be compared directly using `<=>, <, >`, etc. You can create a Time object from a date string by saying `Time.parse("1/1/1984")`. You can assume the `release_date` is always valid.

* Calling `errors.add(:field, "message")` on the model object to be validated adds a validation error associated with the attribute named field, with the explanatory message message; for example, `errors.add(:title, "cannot be blank")`

```ruby
class Movie < ActiveRecord::Base
  # YOUR CODE HERE
end
```

## A possible solution

```ruby
class Movie < ActiveRecord::Base
  validate :valid_mpaa_rating
  validates_inclusion_of :rating, :in => ['G','PG','PG-13','R',  :allow_blank => true
  def valid_mpaa_rating
    if release_date < Time.parse("1 Jan 1970") && !rating.blank?
      errors.add(:rating, "must be blank for films before 1970")
    if release_date < Time.parse("1 Jan 1984") && rating == 'PG-13'
  end
end
