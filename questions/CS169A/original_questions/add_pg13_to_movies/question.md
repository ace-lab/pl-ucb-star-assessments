# Add and validate a field on the RottenPotatoes Movie model

The MPAA rating PG-13 was introduced in 1984.  Enhance the Movie class to check that the "PG-13" rating is only accepted as valid if the movie was released on or after 1-Jan-1984.

Recall that:

* `validate :my_validation_method` calls the instance method my_validation_method on the model object to be validated

* The `release_date` attribute is a Ruby Time object; these can be compared directly using <=>, <, >, etc. You can create a Time object from a date string by saying Time.parse("1/1/1984"). You can assume the release_date is always valid.

* Calling `errors.add(:field, "message")` on the model object to be validated adds a validation error associated with the attribute named field, with the explanatory message message; for example, `errors.add(:title, "cannot be blank")`

NOT ALL BLANKS MAY NEED TO BE FILLED IN, but you shouldn't need to add any blanks.

```ruby
class Movie < ActiveRecord::Base
  _____________
  validate :rating_consistent_with_date
  def ____________()
    pg13_invented = Time.parse "1 Jan 1984"
    if (____________________) and (______________)
       __________.errors.add(:rating, 'only valid for 1984 and later')
    end
    _______________
  end
end
```

