import { LucideIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

interface CategoryCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  href: string;
  gradient?: boolean;
}

const CategoryCard = ({ title, description, icon: Icon, href, gradient }: CategoryCardProps) => {
  return (
    <Link to={href} className="group block">
      <Card className="h-full transition-all duration-300 hover:shadow-large hover:-translate-y-1 border-2 hover:border-primary/20">
        <CardHeader>
          <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-4 ${
            gradient ? 'bg-gradient-accent' : 'bg-gradient-primary'
          } group-hover:scale-110 transition-transform duration-300`}>
            <Icon className="h-7 w-7 text-white" />
          </div>
          <CardTitle className="text-2xl flex items-center justify-between">
            {title}
            <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
          </CardTitle>
          <CardDescription className="text-base">{description}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Click to access {title.toLowerCase()} management
          </p>
        </CardContent>
      </Card>
    </Link>
  );
};

export default CategoryCard;
